import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  title: null,

  curatedChanges: computed('data', function() {
    let actions = this.get('data.actions');
    let summaries = this.get('data.summary');
    let curatedChanges = {};

    Object.keys(actions).forEach((cde) => {
      actions[cde].forEach((op, idx) => {
        if (!curatedChanges[cde]) {
          curatedChanges[cde] = [];
        }

        curatedChanges[cde].push({
          cde,
          accepted: op.accepted,
          summary: summaries[cde][idx]
        });
      });
    });

    return curatedChanges;
  })
});
