import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import { run } from '@ember/runloop';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';
import fetch from 'fetch';
import Config from 'almanac/config/environment';
import { hash } from 'rsvp';

export default Route.extend(AuthenticatedRouteMixin, {
  session: service(),

  model() {
    return hash({
      completedReviews: this.store.query('review', { include: 'user', status: 'Completed' }),
      currentReviews: this.store.query('review', { include: 'user' }).then((reviews) => {
        return reviews.filter((review) => {
          return review.get('status') !== 'Completed';
        })
      })
    });
  },

  actions: {
    removeReview(review) {
      review.destroyRecord().then(() => {
        run.later(() => {
          this.refresh();
        }, 100);
      });
    },
    requestRemoval(review) {
      fetch(`${Config.api.host}/${Config.api.namespace}/reviews/${review.id}/request-removal`, {
        headers: {
          'Authorization': `Bearer ${this.get('session.session.authenticated.token')}`
        }
      }).then((response) => {
        if (response.status === 200) {
          this.get('flashMessages').success('Email sent to request removal of the review.');
        } else {
          this.get('flashMessages').danger('There was an error requesting the removal.');
        }
      });
    },
    checkStatus() {
      this.refresh();
    }
  }
});
