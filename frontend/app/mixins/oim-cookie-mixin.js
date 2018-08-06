import $ from 'jquery';
import { on } from 'rsvp';
import Mixin from '@ember/object/mixin';
import isOimCookieValid from 'almanac/utils/is-oim-cookie-valid';

export default Mixin.create({
  beforeModel() {
    this._super(...arguments);

    on('error', function() {
      if (!isOimCookieValid()) {
        window.location.reload();
      }
    });

    $.ajaxSetup({
      headers: {
        'X-Frame-Options': 'deny'
      },

      error() {
        if (!isOimCookieValid()) {
          window.location.reload();
        }
      }
    });
  },

  actions: {
    /**
     * Handle the error state of the application and redirect
     * to the error page if it has and error message
     *
     * @public
     * @param  {object} error
     */
    error() {
      if (!isOimCookieValid()) {
        window.location.reload();
      }

    }
  }
});
