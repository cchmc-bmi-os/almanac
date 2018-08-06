import Route from '@ember/routing/route';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Route.extend(AuthenticatedRouteMixin, {
  /**
   * Automatically forward to the search route
   * @private
   */
  beforeModel() {
    // replace the history with the search route
    return this.replaceWith('search');
  }
});
