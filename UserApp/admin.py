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





from datetime import date

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





def export_users_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nom', 'Prénom', 'Email', 'Pays', 'Adresse', 'Date Naissance', 'Date Inscription'])

    for user in queryset:
        writer.writerow([
            user.id_user,
            user.nom,
            user.prenom,
            user.email,
            user.pays,
            user.adresse,
            user.date_naissance,
            user.date_joined,
        ])

    return response

export_users_csv.short_description = "Exporter les utilisateurs en CSV"



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'nom', 'prenom', 'is_staff', 'is_superuser', 'date_joined',)
    search_fields = ('email', 'nom', 'prenom')
    list_filter = ('pays', 'is_staff', 'is_superuser', 'date_joined', AgeFilter,)
    actions = [export_users_csv]
    


    fieldsets = (
        ('Informations', {
            'fields': ('email', 'password')
        }),
        ('Détails personnels', {
            'fields': ('nom', 'prenom', 'date_naissance', 'pays', 'adresse')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )

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
    
    