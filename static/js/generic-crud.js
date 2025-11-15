/**
 * Système générique CRUD pour gérer les entités côté front-end
 * Utilisable pour n'importe quel modèle Django
 */
class GenericCRUD {
    constructor(config) {
        this.baseUrl = config.baseUrl || '';
        this.listUrl = config.listUrl || `${this.baseUrl}/api/accommodations/`;
        this.createUrl = config.createUrl || `${this.baseUrl}/api/accommodations/create/`;
        this.updateUrl = config.updateUrl || `${this.baseUrl}/api/accommodations/{id}/update/`;
        this.deleteUrl = config.deleteUrl || `${this.baseUrl}/api/accommodations/{id}/delete/`;
        this.getUrl = config.getUrl || `${this.baseUrl}/api/accommodations/{id}/`;
        this.containerId = config.containerId || 'crud-container';
        this.formId = config.formId || 'crud-form';
        this.onSuccess = config.onSuccess || null;
        this.onError = config.onError || null;
        this.renderItem = config.renderItem || this.defaultRenderItem;
        this.fields = config.fields || [];
        
        this.currentEditId = null;
        this.init();
    }

    init() {
        this.loadList();
        this.setupForm();
    }

    /**
     * Récupère le token CSRF depuis les cookies ou le formulaire
     */
    getCsrfToken() {
        // D'abord, essayer de récupérer depuis le formulaire
        const form = document.getElementById(this.formId);
        if (form) {
            const csrfInput = form.querySelector('[name="csrfmiddlewaretoken"]');
            if (csrfInput) {
                return csrfInput.value;
            }
        }
        
        // Sinon, chercher dans les cookies
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Effectue une requête HTTP
     */
    async request(url, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const result = await response.json();
            return result;
        } catch (error) {
            return {
                success: false,
                message: `Erreur réseau: ${error.message}`
            };
        }
    }

    /**
     * Charge la liste des éléments
     */
    async loadList() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        container.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Chargement...</span></div></div>';

        const result = await this.request(this.listUrl);
        
        if (result.success) {
            this.renderList(result.data);
            if (this.onSuccess) this.onSuccess('list', result.data);
        } else {
            container.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
            if (this.onError) this.onError('list', result.message);
        }
    }

    /**
     * Affiche la liste des éléments
     */
    renderList(items) {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        if (items.length === 0) {
            container.innerHTML = '<div class="alert alert-info">Aucun élément trouvé.</div>';
            return;
        }

        let html = '<div class="row">';
        items.forEach(item => {
            html += this.renderItem(item);
        });
        html += '</div>';
        container.innerHTML = html;

        // Ajouter les événements de modification et suppression
        this.attachItemEvents();
    }

    /**
     * Rendu par défaut d'un élément
     */
    defaultRenderItem(item) {
        return `
            <div class="col-md-4 mb-4" data-id="${item.id}">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${item.titre || item.name || 'Sans titre'}</h5>
                        <p class="card-text">${item.description || ''}</p>
                        <div class="d-flex justify-content-between">
                            <button class="btn btn-sm btn-primary edit-btn" data-id="${item.id}">Modifier</button>
                            <button class="btn btn-sm btn-danger delete-btn" data-id="${item.id}">Supprimer</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Attache les événements aux boutons d'action
     */
    attachItemEvents() {
        // Boutons de modification
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.getAttribute('data-id');
                this.editItem(id);
            });
        });

        // Boutons de suppression
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.getAttribute('data-id');
                this.deleteItem(id);
            });
        });
    }

    /**
     * Configure le formulaire
     */
    setupForm() {
        const form = document.getElementById(this.formId);
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm();
        });

        // Bouton d'annulation
        const cancelBtn = form.querySelector('.cancel-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.resetForm();
            });
        }
    }

    /**
     * Remplit le formulaire avec les données d'un élément
     */
    async editItem(id) {
        this.currentEditId = id;
        const result = await this.request(this.getUrl.replace('{id}', id));

        if (result.success) {
            this.fillForm(result.data);
            if (this.onSuccess) this.onSuccess('get', result.data);
        } else {
            alert(`Erreur: ${result.message}`);
            if (this.onError) this.onError('get', result.message);
        }
    }

    /**
     * Remplit le formulaire avec des données
     */
    fillForm(data) {
        const form = document.getElementById(this.formId);
        if (!form) return;

        // Remplir tous les champs du formulaire
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = data[key];
                } else {
                    field.value = data[key] || '';
                }
            }
        });

        // Changer le titre du formulaire
        const formTitle = form.querySelector('.form-title');
        if (formTitle) {
            formTitle.textContent = 'Modifier l\'accommodation';
        }

        // Changer le texte du bouton submit
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Modifier';
        }

        // Scroll vers le formulaire
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /**
     * Réinitialise le formulaire
     */
    resetForm() {
        const form = document.getElementById(this.formId);
        if (!form) return;

        form.reset();
        this.currentEditId = null;

        // Réinitialiser le titre du formulaire
        const formTitle = form.querySelector('.form-title');
        if (formTitle) {
            formTitle.textContent = 'Ajouter une accommodation';
        }

        // Réinitialiser le texte du bouton submit
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Ajouter';
        }
    }

    /**
     * Soumet le formulaire
     */
    async submitForm() {
        const form = document.getElementById(this.formId);
        if (!form) return;

        const formData = new FormData(form);
        const data = {};

        // Convertir FormData en objet
        for (let [key, value] of formData.entries()) {
            const field = form.querySelector(`[name="${key}"]`);
            // Gérer les checkboxes
            if (field && field.type === 'checkbox') {
                data[key] = field.checked;
            } else {
                data[key] = value;
            }
        }

        // Gérer les checkboxes qui ne sont pas dans FormData (non cochées)
        form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            if (!formData.has(checkbox.name)) {
                data[checkbox.name] = false;
            }
        });

        // Convertir les valeurs numériques
        if (data.prix) {
            data.prix = parseFloat(data.prix);
        }

        let result;
        if (this.currentEditId) {
            // Mise à jour
            result = await this.request(
                this.updateUrl.replace('{id}', this.currentEditId),
                'PUT',
                data
            );
        } else {
            // Création
            result = await this.request(this.createUrl, 'POST', data);
        }

        if (result.success) {
            alert(result.message);
            this.resetForm();
            this.loadList();
            if (this.onSuccess) this.onSuccess(this.currentEditId ? 'update' : 'create', result.data);
        } else {
            alert(`Erreur: ${result.message}`);
            if (this.onError) this.onError(this.currentEditId ? 'update' : 'create', result.message);
        }
    }

    /**
     * Supprime un élément
     */
    async deleteItem(id) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
            return;
        }

        const result = await this.request(
            this.deleteUrl.replace('{id}', id),
            'DELETE'
        );

        if (result.success) {
            alert(result.message);
            this.loadList();
            if (this.onSuccess) this.onSuccess('delete', { id });
        } else {
            alert(`Erreur: ${result.message}`);
            if (this.onError) this.onError('delete', result.message);
        }
    }
}

