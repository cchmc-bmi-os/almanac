import Component from '@ember/component';
import { inject as service } from '@ember/service';
import Config from 'almanac/config/environment';
import Dropzone from "npm:dropzone";
import { A } from '@ember/array';

export default Component.extend({
  session: service(),
  store: service(),
  header: A([]),
  showPreview: false,
  didInsertElement() {
    let _this = this;

    let dropzone = new Dropzone('form#query-file', {
      url: `${Config.api.host}/${Config.api.namespace}/reviews/upload`,
      paramName: 'file',
      maxFilesize: 10000,
      clickable: '.dz-clickable',
      acceptedFiles: 'text/csv,application/vnd.ms-excel',
      headers: {
        'accept': 'application/vnd.api+json',
        'authorization': `Bearer ${this.get('session.session.authenticated.token')}`
      }
    });

    dropzone.on('complete', function(file) {
      if (!file.xhr) {
        _this.$('#query-file .blurb').hide();
        _this.$('#query-file .dz-preview').remove();
        _this.$('#query-file').append('<div class="dz-preview"><h4>File format invalid.</h4></div>');
        return;
      }

      let jsonResponse = JSON.parse(file.xhr.response);
      if (jsonResponse.success) {
        _this.set('header', jsonResponse.header);
        _this.set('data', jsonResponse.data);
        _this.set('location', jsonResponse.location);
        _this.$('#query-file .dz-preview').remove();
        _this.$('#query-file').append('<div class="dz-preview"><h4>Processing Uploaded File...</h4></div>');
        _this.checkHeaders();
      } else {
        _this.$('#query-file .blurb').hide();
        _this.$('#query-file .dz-preview').remove();
        _this.$('#query-file').append(`<div class="dz-preview"><h4>${jsonResponse.message}</h4></div>`);
      }
    });

    dropzone.on('addedfile', function(/* file*/) {
      _this.$('#query-file .blurb').hide();
      _this.$('#query-file .dz-preview').remove();
      _this.$('#query-file').append('<div class="dz-preview"><h4>Extracting file header...</h4></div>');
    });
  },
  checkHeaders() {
    this.$('#query-file .blurb').hide();
    this.$('#query-file .dz-preview').remove();

    // check for same columns
    if (this.get('header').length < 17) {
      this.$('#query-file').append('<div class="dz-preview"><h4>The file does not have at least 17 columns</h4></div>');
      return;
    }

    // check the first 4 columns
    if (!this.get('header')[0].replace(/_+/g, ' ').startsWith('Variable / Field Name')
      && !this.get('header')[1].replace(/_+/g, ' ').startsWith('Form Name')
      && !this.get('header')[2].replace(/_+/g, ' ').startsWith('Section Header')
      && !this.get('header')[3].replace(/_+/g, ' ').startsWith('Field Type')) {
      this.$('#query-file').append('<div class="dz-preview"><h4>The file headers are not correct.</h4></div>');
      return;
    }

    this.$('#query-file').append('<div class="dz-preview text-success"><h4>File uploaded successfully.</h4></div>');
    this.send('fileUploaded');
  },
  actions: {
    fileUploaded() {
      this.set('preview', this.get('data').slice(1, 10));
      this.set('showPreview', true);
      setTimeout(() => {
        window.scrollTo(0, document.getElementById('preview').offsetHeight - 25);
      }, 200);
    },
    submitReview() {
      this.get('store').findRecord('user', this.get('session.data.authenticated.user_id')).then((user) => {
        this.get('submit')({
          name: this.get('name'),
          user,
          data: this.get('data'),
          header: this.get('header'),
          location: this.get('location')
        });
      });
    }
  }
});
