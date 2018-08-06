import Controller from '@ember/controller';
import { task } from 'ember-concurrency';
import Config from 'almanac/config/environment';
import { inject as service } from '@ember/service';


export default Controller.extend({
  session: service(),
  updateButtonText: 'Update DA',
  doUpdateDa: task(function *(siteId) {
    let { token } = this.get('session.data.authenticated');
    let url = `${Config.api.host}/${Config.api.namespace}/reviews/${this.get('model.review.id')}/update/${siteId}`;
    let options = {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    };
    try {
      let response = yield fetch(url, options);
      let json = yield response.json();
      if (json.errors) {
        this.set('updateError', json.errors[0].title);
        this.set('updateButtonText', 'An error occurred');
      } else {
        this.set('updateButtonText', 'DA Update Complete!');
      }
    } catch(e) {
      this.set('updateError', e.errors[0].title);
      this.set('updateButtonText', 'An error occurred');
    }
  }),

  actions: {
    createSite(site) {
      let newSite = this.store.createRecord('site', {
        name: site,
        display: site,
        pi: '   ',
        is_live: true
      });

      newSite.save().then(() => {
        this.send('refreshModel');
        this.set('selectedSite', newSite);
      })
    },

    updateDa() {
      if (this.get('doUpdateDat.isRunning')) {
        return;
      }

      let site = this.get('selectedSite');

      if (!site) {
        return;
      }

      this.get('doUpdateDa').perform(site.get('id'));
    }
  }
});
