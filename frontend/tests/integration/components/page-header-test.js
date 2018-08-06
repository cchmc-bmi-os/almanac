import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, findAll } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | page header', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    this.set('showReview', false);
    this.set('session', { isAuthenticated: false });

    await render(hbs`{{page-header showReview=showReview session=session}}`);

    assert.ok(find('.header'))
    assert.equal(findAll('#main-menu .navbar-nav').length, 2, 'it has two navs');
    assert.equal(findAll('#main-menu .navbar-nav .nav-item').length, 3, 'it has three nav items');
    assert.ok(findAll('#main-menu .navbar-nav.mr-auto'), 'it has one navbar-nav aligned right');

    this.set('showReview', true);
    assert.equal(findAll('#main-menu .navbar-nav .nav-item').length, 4, 'it now has four nav items');

    this.set('session', { isAuthenticated: true });
    assert.equal(findAll('#main-menu .navbar-nav .nav-item').length, 5, 'it now has five nav items');
  });
});
