import Route from '@ember/routing/route';
import RSVP from 'rsvp';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';
import Config from 'almanac/config/environment';
import { get } from '@ember/object';

export default Route.extend(AuthenticatedRouteMixin, {
  model(params) {
    return RSVP.hash({
      reviewVersion: this.store.query('review-version', { review__id: params.review, include: 'review' }).then((versions) => {
        return versions.get('firstObject');
      }),
      type: params.type,
      conditions: this.store.findAll('condition')
    });
  },
  setupController(controller, model) {
    this._super(...arguments);

    let reviewType = model.reviewVersion.get('review.status').replace(' Review', '');
    controller.set('reviewType', reviewType);

    if (!Config.review.roles) {
      throw new Error('Please specify roles for the review in the config');
    }

    controller.set('reviewCanBeFinished', Config.review.roles.includes(reviewType));
    controller.set('reviewRoles', Config.review.roles);

    // setup the defaultConditions stuff
    let content = model.reviewVersion.get('contents');
    controller.set('defaultConditions', get(content, 'defaultConditions') || []);
    content = null;
  },
  resetController(controller, isExiting) {
    if (isExiting) {
      controller.set('showDoneConfirmation', false);
    }
  }
});
