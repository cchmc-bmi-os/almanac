import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import DS from 'ember-data';
import Config from 'almanac/config/environment';

const { attr, belongsTo, hasMany } = DS;

export default DS.Model.extend({
  session: service(),
  name: attr('string'),
  status: attr('string'),
  location: attr('string'),
  started_at: attr('moment-date'),
  completed_at: attr('moment-date'),
  updated_da_summary: attr('json'),

  user: belongsTo('user', { async: true }),
  versions: hasMany('review-version', { async: true }),

  isReviewing: computed('status', {
    get() {
      return this.get('status') === 'Grantee Review';
    }
  }),

  isComplete: computed('status', {
    get() {
      return this.get('status') === 'Completed';
    }
  }),

  canActOn: computed('status', 'user', {
    get() {
      let status = this.get('status');
      let userId = this.get('session.data.authenticated.user_id');

      // if the grantee is the status check the review uploader
      if (status === 'Grantee Review' && userId === parseInt(this.get('user.id'))) {
        return true;
      }

      // check the review roles
      return this.get('store').query('review-role', { user__id: userId }).then((roles) => {
        let canAccess = false;
        roles.forEach((role) => {
          if (status.indexOf(role.get('role')) !== -1) {
            canAccess = true;
          } else if (status === 'Grantee Review' && role.get('role') === Config.review.admin) {
            canAccess = true;
          }
        });

        // return the status.
        this.set('canActOn', canAccess);
        return canAccess;
      });
    }
  }),

  canRemove: computed('user', {
    get() {
      let userId = this.get('session.data.authenticated.user_id');

      this.get('store').query('review-role', { user__id: userId }).then((roles) => {
        let canRemove = false;
        roles.forEach((role) => {
          if (role.get('role') === Config.review.admin) {
            canRemove = true;
          }
        });

        this.set('canRemove', canRemove);
      });
    }
  }),

  currentVersion: computed('versions', {
    get() {
      let version = null;
      this.get('versions').forEach((dbVersion) => {
        if (version === null || version.version > dbVersion.version) {
          version = dbVersion;
        }
      });

      return version;
    }
  }),

  isReadyForAnnotation: computed('status', {
    get() {
      let status = this.get('status');

      return status !== 'Calculating Diff';
    }
  }),

  refreshVersions() {
    this.reload();
    let versionsRef = this.hasMany('versions');
    versionsRef.load().then(() => {
      this.propertyDidChange('versions');
    });
  }
});
