import EmberRouter from '@ember/routing/router';
import config from './config/environment';

const Router = EmberRouter.extend({
  location: config.locationType,
  rootURL: config.rootURL
});

Router.map(function() {
  this.route('login');
  this.route('denied');
  this.route('search');
  this.route('help');
  this.route('cde-view', { path: '/view/LPDR/:cde' }, function() {
    this.route('info', { path: 'info' });
    this.route('codes', { path: 'codes' });
    this.route('visibility', { path: 'visibility' });
  });
  this.route('cde-version', { path: '/view/version/LPDR/:cde' });

  if (['development', 'dev-lpdr', 'test-lpdr'].indexOf(config.environment) !== -1) {
    this.route('review', function() {
      this.route('upload');
      this.route('annotate', { path: '/:review/annotate/:type' });
      this.route('info', { path: '/:review/info' });
    });
  }

  this.route('not-found', { path: '*path' });
  this.route('error');
});

export default Router;
