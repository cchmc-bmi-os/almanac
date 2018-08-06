import Config from 'almanac/config/environment';

export default function() {
  this.urlPrefix = Config.api.host;
  this.namespace = Config.api.namespace;
  this.timing = 200;

  this.post('auth', { token: '8374hg8734ghh2348g', user_id: 1 }, 200);
  this.delete('auth', {}, 204);

  this.get('forms');
  this.get('condition-categories');
  this.get('conditions');
  this.get('sites');
  this.get('saved-cdes');

  this.get('reviews');
  this.get('reviews/:id');
  this.get('review-roles');
  this.get('review-roles/:id');

  // These comments are here to help you get started. Feel free to delete them.

  /*
    Config (with defaults).

    Note: these only affect routes defined *after* them!
  */

  // this.urlPrefix = '';    // make this `http://localhost:8080`, for example, if your API is on a different server
  // this.namespace = '';    // make this `api`, for example, if your API is namespaced
  // this.timing = 400;      // delay for each request, automatically set to 0 during testing

  /*
    Shorthand cheatsheet:

    this.get('/posts');
    this.post('/posts');
    this.get('/posts/:id');
    this.put('/posts/:id'); // or this.patch
    this.del('/posts/:id');
  */
}
