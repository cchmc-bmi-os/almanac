import Component from '@ember/component';
import { inject as service } from '@ember/service';
import { computed } from '@ember/object';
import Config from 'almanac/config/environment';

export default Component.extend({
  // the session service for authentication used for logout
  session: service(),
  rootURL: Config.rootURL,
  showReview: computed('Config', {
    get() {
      return ['development', 'dev-lpdr', 'test-lpdr'].indexOf(Config.environment) !== -1;
    }
  }),

  actions: {
    invalidateSession() {
      this.get('session').invalidate();
    }
  }
});
