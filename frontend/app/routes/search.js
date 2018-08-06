import Route from '@ember/routing/route';
import { hash } from 'rsvp';
import { inject as service } from '@ember/service';
import { isEmpty } from '@ember/utils';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Route.extend(AuthenticatedRouteMixin, {
  // the session service for authentication
  session: service(),

  // the search-filters service
  searchFilters: service('search-filters'),

  // the saved-cdes service
  savedCdes: service('saved-cdes'),

  /**
   * Fetch the needed data for the search filters and saved cde display
   * @private
   */
  model() {
    return hash({
      sites: this.store.findAll('site'),
      conditions: this.store.findAll('condition'),
      conditionCategories: this.store.findAll('condition-category'),
      forms: this.store.findAll('form'),
      settings: this.store.find('setting', 1)
    });
  },

  /**
   * Setup the controller variables
   *
   * @private
   * @param  {object} controller
   * @param  {object} model
   */
  setupController(controller, model) {
    this._super(...arguments);

    // calculate forms to display
    let forms = [];
    controller.set('forms', model.forms.filter((form) => {
      let include = forms.indexOf(form.get('name')) === -1;
      forms.push(form.get('name'));
      return include;
    }));
    forms = null;

    // calculate the sections to display
    controller.set('sections', model.forms.filter((form) => {
      return !isEmpty(form.get('section'));
    }));

    // setup other data for the filtesr
    controller.set('sites', model.sites);
    controller.set('conditions', model.conditions);
    controller.set('conditionCategories', model.conditionCategories);
    controller.set('siteQuestions', null);

    // setup the saved filters
    this.get('searchFilters').loadFilters();
    this.get('searchFilters').saveFilter('page', 1);

    // setup the initial view data
    controller.set('showResults', false);

    this.store.find('saved-cde', this.get('session.data.authenticated.user_id')).then((savedCde) => {
      this.set('savedCdes.sourceData', savedCde);
      this.get('savedCdes').collapseForms();
    });
  }
});
