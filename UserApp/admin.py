# UserApp/admin.py
from django.contrib import admin
from .models import User
from django.utils import timezone
from django.http import HttpResponse
import csv
from datetime import date, timedelta
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpResponseRedirect
import json
from calendar import monthrange
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER
import os
from django.conf import settings
from datetime import datetime
from .ai_security import run_ai_security    
from datetime import date
from .ai_security import retrain_model
from django.contrib import messages
from django.utils import timezone
class AgeFilter(admin.SimpleListFilter):
    title = 'Âge'
    parameter_name = 'age'

    def lookups(self, request, model_admin):
        return [
            ('moins18', 'Moins de 18 ans'),
            ('18_30', '18 - 30 ans'),
            ('30_50', '30 - 50 ans'),
            ('plus50', 'Plus de 50 ans'),
        ]

    def _years_ago(self, years):
        """Retourne la date correspondant à aujourd'hui moins `years` années.
        Gère les cas de 29 février en tombant au 28 si nécessaire."""
        today = date.today()
        try:
            return date(today.year - years, today.month, today.day)
        except ValueError:
            # Ex: 29 février — ramener au 28
            return date(today.year - years, today.month, 28)

    def queryset(self, request, queryset):
        # Ne pas toucher les utilisateurs sans date_naissance (on peut les exclure)
        if self.value() == 'moins18':
            cutoff = self._years_ago(18)
            # né après cutoff => age < 18
            return queryset.filter(date_naissance__gt=cutoff)

        if self.value() == '18_30':
            upper = self._years_ago(18)   # né <= upper -> >=18
            lower = self._years_ago(30)   # né >= lower -> <=30
            return queryset.filter(date_naissance__lte=upper, date_naissance__gte=lower)

        if self.value() == '30_50':
            upper = self._years_ago(30)
            lower = self._years_ago(50)
            return queryset.filter(date_naissance__lte=upper, date_naissance__gte=lower)

        if self.value() == 'plus50':
            cutoff = self._years_ago(50)
            # né avant ou égal cutoff => age >= 50
            return queryset.filter(date_naissance__lte=cutoff)

        return queryset









@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'nom', 'prenom', 'is_staff', 'is_superuser', 
        'risk_badge', 'score_display', 'last_login_display', 'date_joined'
    )
    search_fields = ('email', 'nom', 'prenom')
    list_filter = ('ai_risk_level', 'pays', 'is_staff', 'is_superuser', 'date_joined', AgeFilter)
    ordering = ('-ai_security_score',)
    actions = ['lancer_ia_securite', 'reentrainer_modele', 'export_users_pdf']
    
    fieldsets = (
        ('🔐 Authentification', {
            'fields': ('email', 'password')
        }),
        ('👤 Informations personnelles', {
            'fields': ('nom', 'prenom', 'date_naissance', 'pays', 'adresse')
        }),
        ('🛡️ Sécurité IA', {
            'fields': ('ai_security_score', 'ai_risk_level'),
            'classes': ('collapse',)
        }),
        ('⚙️ Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    readonly_fields = ('ai_security_score', 'ai_risk_level')
    
    def save_model(self, request, obj, form, change):
        if not obj.username:
            obj.username = obj.email
        super().save_model(request, obj, form, change)
    
    def risk_badge(self, obj):
        """Affichage coloré du niveau de risque"""
        colors_map = {
            'low': '#4caf50',
            'medium': '#ff9800',
            'high': '#f44336',
            'critical': '#b71c1c'
        }
        icons = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }
        color = colors_map.get(obj.ai_risk_level, 'gray')
        icon = icons.get(obj.ai_risk_level, '⚪')
        
        return format_html(
            '<span style="background:{};color:white;padding:6px 12px;'
            'border-radius:15px;font-weight:bold;font-size:11px;">'
            '{} {}</span>',
            color, icon, obj.ai_risk_level.upper()
        )
    risk_badge.short_description = "🛡️ Niveau de risque"
    
    def score_display(self, obj):
        """Affichage du score avec barre de progression"""
        score = obj.ai_security_score
        if score < 30:
            color = '#4caf50'
        elif score < 50:
            color = '#ff9800'
        elif score < 70:
            color = '#f44336'
        else:
            color = '#b71c1c'
        
        return format_html(
            '<div style="width:100px;background:#e0e0e0;border-radius:10px;overflow:hidden;">'
            '<div style="width:{}%;background:{};color:white;'
            'padding:4px;text-align:center;font-weight:bold;font-size:11px;">'
            '{}</div></div>',
            score, color, score
        )
    score_display.short_description = "📊 Score IA"
    
    def last_login_display(self, obj):
        """Affichage de la dernière connexion avec couleur"""
        if not obj.last_login:
            return format_html('<span style="color:#f44336;">❌ Jamais</span>')
        
        from django.utils import timezone
        days = (timezone.now() - obj.last_login).days
        
        if days == 0:
            return format_html('<span style="color:#4caf50;">✅ Aujourd\'hui</span>')
        elif days < 7:
            return format_html('<span style="color:#4caf50;">✅ Il y a {}j</span>', days)
        elif days < 30:
            return format_html('<span style="color:#ff9800;">⚠️ Il y a {}j</span>', days)
        else:
            return format_html('<span style="color:#f44336;">❌ Il y a {}j</span>', days)
    
    last_login_display.short_description = "🕒 Dernière connexion"
    
    # ACTIONS IA
    def lancer_ia_securite(self, request, queryset):
        """Lance l'analyse IA avec Machine Learning"""
        try:
            results = run_ai_security()
            message = (
                f"✅ Analyse IA (Machine Learning) terminée! "
                f"📊 {results['total']} utilisateurs analysés - "
                f"🔴 Critical: {results['critical']} | "
                f"🟠 High: {results['high']} | "
                f"🟡 Medium: {results['medium']} | "
                f"🟢 Low: {results['low']} - "
                f"📈 Score moyen: {results['avg_score']:.1f}/100"
            )
            self.message_user(request, message, level=messages.SUCCESS)
        except Exception as e:
            self.message_user(
                request, 
                f"❌ Erreur lors de l'analyse IA: {str(e)}", 
                level=messages.ERROR
            )
    lancer_ia_securite.short_description = " LANCER L'IA DE SÉCURITÉ"
    

    def export_users_pdf(modeladmin, request, queryset):
        # Créer la réponse HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="utilisateurs_{}.pdf"'.format(
            datetime.now().strftime('%Y%m%d_%H%M%S')
        )

        # Créer le document PDF en paysage pour plus d'espace
        doc = SimpleDocTemplate(response, pagesize=landscape(A4),
                            rightMargin=1*cm, leftMargin=1*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
        
        # Container pour les éléments du PDF
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Ajouter le logo (ajustez le chemin vers votre logo)
        logo_path = os.path.join(settings.MEDIA_ROOT, 'static/public/toonice-logo.png')  
        # Ou utilisez : logo_path = os.path.join(settings.STATIC_ROOT, 'images/logo.png')
        
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=4*cm, height=4*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 0.5*cm))
        
        # Titre
        title = Paragraph("Liste des Utilisateurs", title_style)
        elements.append(title)
        
        # Sous-titre avec date
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#7F8C8D'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        subtitle = Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - Total: {queryset.count()} utilisateurs",
            subtitle_style
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 1*cm))
        
        # Préparer les données du tableau
        data = [['ID', 'Nom', 'Prénom', 'Email', 'Pays', 'Adresse', 'Date Naissance', 'Date Inscription']]
        
        for user in queryset:
            data.append([
                str(user.id_user),
                user.nom or '',
                user.prenom or '',
                user.email or '',
                user.pays or '',
                user.adresse or '',
                user.date_naissance.strftime('%d/%m/%Y') if user.date_naissance else '',
                user.date_joined.strftime('%d/%m/%Y') if user.date_joined else '',
            ])
        
        # Créer le tableau
        table = Table(data, repeatRows=1)
        
        # Style du tableau
        table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Corps du tableau
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Bordures
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2C3E50')),
            
            # Alternance de couleurs pour les lignes
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
        ]))
        
        elements.append(table)
        
        # Footer
        elements.append(Spacer(1, 1*cm))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#95A5A6'),
            alignment=TA_CENTER
        )
        footer = Paragraph("Document confidentiel - Tous droits réservés © 2025", footer_style)
        elements.append(footer)
        
        # Construire le PDF
        doc.build(elements)
        
        return response

    export_users_pdf.short_description = "Exporter les utilisateurs en PDF"




    def reentrainer_modele(self, request, queryset):
        """Force le réentraînement complet des modèles d'IA"""
        try:
            results = retrain_model()
            message = (
                f"✅ Modèles d'IA réentraînés avec succès! "
                f"🧠 Les modèles ont appris de {results['total']} utilisateurs - "
                f"🔴 Critical: {results['critical']} | "
                f"🟠 High: {results['high']} | "
                f"🟡 Medium: {results['medium']} | "
                f"🟢 Low: {results['low']}"
            )
            self.message_user(request, message, level=messages.SUCCESS)
        except Exception as e:
            self.message_user(
                request,
                f"❌ Erreur lors du réentraînement: {str(e)}",
                level=messages.ERROR
            )
    reentrainer_modele.short_description = " RÉENTRAÎNER LES MODÈLES D'IA"

    change_list_template = "changelist.html"
    
    def changelist_view(self, request, extra_context=None):
        period = request.GET.get('period', 'all')
        today = timezone.now().date()
        
        # Première inscription
        first_user = User.objects.order_by('date_joined').first()
        first_date = first_user.date_joined.date() if first_user else today
        
        # Définir les périodes
        periods = {
            'all': {'days': None, 'label': 'Depuis le début'},
            '7days': {'days': 7, 'label': '7 derniers jours'},
            '30days': {'days': 30, 'label': '30 derniers jours'},
            '3months': {'days': 90, 'label': '3 derniers mois'},
            '6months': {'days': 180, 'label': '6 derniers mois'},
            '12months': {'days': 365, 'label': '12 derniers mois'},
        }
        
        selected_period = periods.get(period, periods['all'])
        
        # Calculer dates
        if period == 'all':
            start_date = first_date
        else:
            start_date = today - timedelta(days=selected_period['days'] - 1)
        
        # Stats globales
        total_users = User.objects.count()
        today_count = User.objects.filter(date_joined__date=today).count()
        period_count = User.objects.filter(date_joined__date__gte=start_date).count()
        
        # ========== CALCUL CROISSANCE MENSUELLE ==========
        # Mois actuel
        current_month_start = date(today.year, today.month, 1)
        current_month_count = User.objects.filter(
            date_joined__date__gte=current_month_start,
            date_joined__date__lte=today
        ).count()
        
        # Mois précédent
        if today.month == 1:
            prev_month_year = today.year - 1
            prev_month = 12
        else:
            prev_month_year = today.year
            prev_month = today.month - 1
        
        prev_month_start = date(prev_month_year, prev_month, 1)
        prev_month_days = monthrange(prev_month_year, prev_month)[1]
        prev_month_end = date(prev_month_year, prev_month, prev_month_days)
        
        prev_month_count = User.objects.filter(
            date_joined__date__gte=prev_month_start,
            date_joined__date__lte=prev_month_end
        ).count()
        
        # Calculer le pourcentage
        growth_percent = 0
        if prev_month_count > 0:
            growth_percent = ((current_month_count - prev_month_count) / prev_month_count) * 100
        elif current_month_count > 0:
            growth_percent = 100
        
        # Formater
        if growth_percent > 0:
            growth_text = f"+{growth_percent:.1f}"
            growth_icon = "📈"
            growth_class = "positive"
        elif growth_percent < 0:
            growth_text = f"{growth_percent:.1f}"
            growth_icon = "📉"
            growth_class = "negative"
        else:
            growth_text = "0.0"
            growth_icon = "➖"
            growth_class = "neutral"
        
        # ========== DONNÉES GRAPHIQUE ==========
        daily_data = User.objects.filter(
            date_joined__date__gte=start_date
        ).annotate(
            day=TruncDate('date_joined')
        ).values('day').annotate(
            count=Count('id_user')
        ).order_by('day')
        
        # Remplir tous les jours
        date_counts = {}
        current_date = start_date
        while current_date <= today:
            date_counts[current_date] = 0
            current_date += timedelta(days=1)
        
        for item in daily_data:
            date_counts[item['day']] = item['count']
        
        sorted_dates = sorted(date_counts.keys())
        
        # Format des labels
        if len(sorted_dates) <= 31:
            chart_labels = [d.strftime('%d/%m') for d in sorted_dates]
        elif len(sorted_dates) <= 90:
            chart_labels = [d.strftime('%d/%m') for d in sorted_dates]
        else:
            chart_labels = [d.strftime('%d/%m/%y') for d in sorted_dates]
        
        chart_data = [date_counts[d] for d in sorted_dates]
        
        # JSON
        chart_labels_json = json.dumps(chart_labels)
        chart_data_json = json.dumps(chart_data)
        
        # DEBUG - Afficher dans la console serveur
        print(f"\n{'='*50}")
        print(f"PÉRIODE SÉLECTIONNÉE: {period}")
        print(f"Date début: {start_date} | Date fin: {today}")
        print(f"Nombre de jours: {len(sorted_dates)}")
        print(f"Nombre d'inscriptions: {period_count}")
        print(f"Données: {chart_data[:10]}..." if len(chart_data) > 10 else f"Données: {chart_data}")
        print(f"{'='*50}\n")
        
        # HTML
        stats_html = f"""
        <div class="stats-dashboard">
            <div class="stats-header">
                <h2>📊 Statistiques des inscriptions</h2>
                <div class="period-selector">
                    <select id="periodSelect" onchange="changePeriod(this.value)">
                        <option value="all" {'selected' if period == 'all' else ''}>📊 Depuis le début</option>
                        <option value="7days" {'selected' if period == '7days' else ''}>7 derniers jours</option>
                        <option value="30days" {'selected' if period == '30days' else ''}>30 derniers jours</option>
                        <option value="3months" {'selected' if period == '3months' else ''}>3 derniers mois</option>
                        <option value="6months" {'selected' if period == '6months' else ''}>6 derniers mois</option>
                        <option value="12months" {'selected' if period == '12months' else ''}>12 derniers mois</option>
                    </select>
                </div>
            </div>
            
            <div class="stats-cards">
                <div class="stat-card total">
                    <div class="stat-icon">👥</div>
                    <div class="stat-content">
                        <div class="stat-value">{total_users}</div>
                        <div class="stat-label">Total utilisateurs</div>
                    </div>
                </div>
                
                <div class="stat-card today">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-content">
                        <div class="stat-value">{today_count}</div>
                        <div class="stat-label">Aujourd'hui</div>
                    </div>
                </div>
                
                <div class="stat-card period">
                    <div class="stat-icon">📈</div>
                    <div class="stat-content">
                        <div class="stat-value">{period_count}</div>
                        <div class="stat-label">{selected_period['label']}</div>
                    </div>
                </div>
                
                <div class="stat-card growth {growth_class}">
                    <div class="stat-icon">{growth_icon}</div>
                    <div class="stat-content">
                        <div class="stat-value">{growth_text}%</div>
                        <div class="stat-label">Croissance</div>
                        <div class="stat-comparison">{current_month_count} ce mois vs {prev_month_count} mois dernier</div>
                    </div>
                </div>
            </div>
            
            <div class="chart-wrapper">
                <div class="chart-header">
                    <h3>📈 Évolution - {selected_period['label']}</h3>
                    <div class="chart-info">
                        <span class="info-badge">{period_count} inscriptions</span>
                        <span class="info-badge period-badge">{start_date.strftime('%d/%m/%Y')} → {today.strftime('%d/%m/%Y')}</span>
                    </div>
                </div>
                <div style="background: white; border-radius: 10px; padding: 20px;">
                    <canvas id="userChart" width="400" height="300"></canvas>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <script>
        console.log('=== DEBUT SCRIPT ===');
        console.log('Période actuelle:', '{period}');
        console.log('Labels:', {chart_labels_json});
        console.log('Data:', {chart_data_json});
        
        
        // Fonction pour changer de période
        function changePeriod(newPeriod) {{
            console.log('Changement vers:', newPeriod);
            var currentUrl = window.location.href.split('?')[0];
            window.location.href = currentUrl + '?period=' + newPeriod;
        }}
        
        setTimeout(function() {{
            console.log('Tentative création graphique...');
            
            var canvas = document.getElementById('userChart');
            console.log('Canvas trouvé:', canvas ? 'OUI' : 'NON');
            
            if (!canvas) {{
                alert('ERREUR: Canvas introuvable!');
                return;
            }}
            
            if (typeof Chart === 'undefined') {{
                alert('ERREUR: Chart.js non chargé!');
                console.error('Chart.js non disponible');
                return;
            }}
            
            console.log('Chart.js disponible, création...');
            
            try {{
                var ctx = canvas.getContext('2d');
                
                var myChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {chart_labels_json},
                        datasets: [{{
                            label: 'Inscriptions',
                            data: {chart_data_json},
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.2)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {{
                            legend: {{
                                display: true
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                ticks: {{
                                    precision: 0
                                }}
                            }}
                        }}
                    }}
                }});
                
                console.log('✅ GRAPHIQUE CRÉÉ AVEC SUCCÈS!', myChart);
                
            }} catch(e) {{
                console.error('ERREUR création graphique:', e);
                alert('Erreur: ' + e.message);
            }}
        }}, 1000);
        </script>
        
        <style>
        .stats-dashboard {{
            background: #fff;
            border-radius: 16px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        }}
        .stats-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .stats-header h2 {{
            margin: 0;
            font-size: 28px;
            color: #2c3e50;
            font-weight: 700;
        }}
        .period-selector select {{
            padding: 12px 20px;
            border: 2px solid #667eea;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            color: #667eea;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .period-selector select:hover {{
            background: #667eea;
            color: white;
        }}
        .stats-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 35px;
        }}
        .stat-card {{
            border-radius: 14px;
            padding: 28px;
            display: flex;
            align-items: center;
            gap: 20px;
            box-shadow: 0 6px 20px rgba(102,126,234,0.25);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card.total {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .stat-card.today {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .stat-card.period {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .stat-card.growth.positive {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        .stat-card.growth.negative {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        .stat-card.growth.neutral {{ background: linear-gradient(135deg, #a8a8a8 0%, #c0c0c0 100%); }}
        .stat-icon {{ font-size: 42px; }}
        .stat-value {{
            font-size: 34px;
            font-weight: 800;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-label {{
            font-size: 13px;
            color: rgba(255,255,255,0.95);
            margin-top: 6px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .stat-comparison {{
            font-size: 11px;
            color: rgba(255,255,255,0.8);
            margin-top: 4px;
        }}
        .chart-wrapper {{
            background: linear-gradient(to bottom, #f8f9fb, #fff);
            border-radius: 14px;
            padding: 25px;
            border: 1px solid #e8ecf1;
        }}
        .chart-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .chart-header h3 {{
            margin: 0;
            font-size: 20px;
            color: #2c3e50;
            font-weight: 700;
        }}
        .chart-info {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        .info-badge {{
            background: #667eea;
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
        }}
        .period-badge {{ background: #764ba2; }}
        @media (max-width: 768px) {{
            .stats-cards {{ grid-template-columns: 1fr; }}
            .chart-header {{ flex-direction: column; align-items: flex-start; }}
        }}
        </style>
        """
        
        extra_context = extra_context or {}
        extra_context['stats_block'] = mark_safe(stats_html)
        return super().changelist_view(request, extra_context=extra_context)
    
    