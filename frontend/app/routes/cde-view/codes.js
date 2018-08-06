import $ from 'jquery';
import Route from '@ember/routing/route';
import { run } from '@ember/runloop';

export default Route.extend({
  actions: {
    didTransition() {
      run.later(() => {
        $('[data-toggle="tooltip"]').tooltip();
      }, 1000);
    }
  }
});
