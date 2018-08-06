import Route from '@ember/routing/route';

export default Route.extend({
  model(params) {
    return this.store.queryRecord('question-detail', { name: params.cde }).catch(() => {
      this.get('flashMessages').danger('Could not find CDE');
      this.transitionTo('search');
    });
  }
});
