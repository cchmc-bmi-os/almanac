import Route from '@ember/routing/route';
import ApplicationRouteMixin from 'ember-simple-auth/mixins/application-route-mixin';
import Config from 'almanac/config/environment';
import OimCookieMixin from 'almanac/mixins/oim-cookie-mixin';

export default Route.extend(ApplicationRouteMixin, OimCookieMixin, {
  sessionInvalidated() {
    if (['development', 'testing', 'bmilpdralmt1'].indexOf(Config.environment) === -1) {
      window.location.replace('https://login.research.cchmc.org/pub/logout.aspx');
    }
  },
  actions: {
    error(error) {
      Bugsnag.notifyException(error);

      if (error) {
        this.transitionTo('error');
      }
    }
  }
});
