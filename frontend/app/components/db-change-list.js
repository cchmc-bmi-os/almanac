import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  changes: computed('version', 'accepted', {
    get() {
      let notFound = [];
      let changed = [];

      // get all the not found cdes
      let notFoundCdes = [];
      if (this.get('accepted.not_found')) {
        notFoundCdes = this.get('accepted.not_found').map((cde) => cde[0]);
      }

      // get all of the changed cdes
      let changedCdes = [];
      if (this.get('accepted.not_found')) {
        changedCdes = this.get('accepted.different').map((cde) => cde[0]);
      }

      // map all of them to right section
      if (this.get('version.contents')) {
        this.get('version.contents').forEach((cde) => {
          if (notFoundCdes.indexOf(cde[0]) !== -1) {
            notFound.push({
              name: cde[0],
              type: cde[3],
              text: cde[4],
              chouces: cde[5].split(' | ')
            });
          } else if (changedCdes.indexOf(cde[0]) !== -1) {
            changed.push({
              name: cde[0],
              type: cde[3],
              text: cde[4],
              chouces: cde[5].split(' | ')
            });
          }
        });
      }

      return {
        adds: notFound,
        updates: changed
      };
    }
  })
});
