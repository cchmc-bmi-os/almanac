import Route from '@ember/routing/route';
import RSVP from 'rsvp';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Config from 'almanac/config/environment';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';
import isReviewAdmin from 'almanac/utils/is-review-admin';
import fetch from 'fetch';

export default Route.extend(AuthenticatedRouteMixin, {
  session: service(),

  model(params) {
    return RSVP.hash({
      review: this.store.find('review', params.review),
      reviewVersions: this.store.query('review-version', { reivew__id: params.review }),
      sites: this.store.findAll('site')
    });
  },
  setupController(controller, model) {
    this._super(...arguments);
    this.controllerFor('review').set('showUpload', false);

    controller.set('isAdmin', isReviewAdmin(this.get('session'), this.store));
    controller.set('finalDd', model.reviewVersions.get('firstObject'));
    // always the previous version
    controller.set('changes', model.reviewVersions.objectAt(1));
    controller.set('siteName', model.review.get('name'));
    controller.set('siteSuffix', computed('siteName', {
      get() {
        return this.get('siteName').replace(/\W+/g, '').toLowerCase().substring(0, 8);
      }
    }));
    controller.set('exportUrl', `${Config.api.host}/${Config.api.namespace}/reviews/${model.review.id}/export`);
    controller.set('updateDaUrl', `${Config.api.host}/${Config.api.namespace}/reviews/${model.review.id}/update?site=`);
  },

  actions: {
    updateDa() {
      this.controller.set('updatingDa', true);
      fetch(`${this.controller.get('updateDaUrl')}${this.controller.siteName}`).then(() => {
        this.refresh();
        this.controller.set('updatingDa', false);
        this.controller.set('showUpdateDa', false);
      }, () => {
        this.get('flashMessages').danger('There was an error when updating the DA');
      });
    },

    refreshModel() {
      this.refresh();
    }
  }
});
