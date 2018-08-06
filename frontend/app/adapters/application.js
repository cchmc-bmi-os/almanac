import DS from 'ember-data';
import Config from 'almanac/config/environment';
import DataAdapterMixin from 'ember-simple-auth/mixins/data-adapter-mixin';

export default DS.JSONAPIAdapter.extend(DataAdapterMixin, {
  namespace: Config.api.namespace,
  host: Config.api.host,

  authorize(xhr) {
    let { token } = this.get('session.data.authenticated');
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
  }
});
