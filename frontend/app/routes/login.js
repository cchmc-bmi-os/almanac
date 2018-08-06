import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  // the session service for authentication
  session: service(),

  /**
   * Try to authenticate the user based on the headers and redirect
   * to the denied route if it cannot authenticate
   *
   * @private
   */
  beforeModel() {
    this.get('session').authenticate('authenticator:application').catch(() => {
      this.transitionTo('denied');
    });
  }
});
