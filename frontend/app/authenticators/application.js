import $ from 'jquery';
import { run } from '@ember/runloop';
import { isEmpty } from '@ember/utils';
import { Promise } from 'rsvp';
import Base from 'ember-simple-auth/authenticators/base';
import Config from 'almanac/config/environment';

export default Base.extend({
  /**
   * This will test to see if the current session data has the required
   * token property for authentication
   *
   * @public
   * @param  {object} data
   */
  restore(data) {
    return new Promise((resolve, reject) => {
      if (!isEmpty(data.token)) {
        resolve(data);
      } else {
        reject();
      }
    });
  },

  /**
   * This will authenticate to the provided authentication endpoint defined in the
   * config.  It doesn't pass any data due to the header authentication that the
   * API uses.
   *
   * @public
   */
  authenticate(/* args*/) {
    return new Promise((resolve, reject) => {
      $.ajax({
        url: `${Config.api.host}/${Config.api.namespace}/${Config.api.auth}`,
        type: 'POST',
        data: {},
        dataType: 'json'
      }).then((response) => {
        if (!isEmpty(response.token)) {
          // success token exists
          run(() => {
            resolve({
              token: response.token,
              user_id: response.user_id
            });
          });
        } else {
          // error no token
          run(() => {
            reject({
              error: response.message,
              code: 401
            });
          });
        }
      }, (xhr, status, error) => {
        run(() => {
          reject({
            error, code: 400
          });
        });
      });
    });
  },

  /**
   * This will invalidate the session by making a delete request.  No matter what
   * it will invalidate the session and refresh the page.
   *
   * @public
   */
  invalidate(/* data */) {
    return new Promise((resolve) => {
      $.ajax({
        url: `${Config.api.host}/${Config.api.namespace}/${Config.api.auth}`,
        type: 'DELETE'
      }).always(() => {
        resolve();
      });
    });
  }
});
