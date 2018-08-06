import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';
import moment from 'moment';

module('Integration | Component | page footer', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    this.set('version', '1.1.1');
    this.set('lastUpdatedDate', '2016-10-18');
    let expectedWording = `©${moment().format('YYYY')} Cincinnati Children's Hospital Medical Center 3333 Burnet Avenue, Cincinnati, Ohio 45229-3039, Hosted by Biomedical Informatics, Version: 1.1.1, Last Updated: 2016-10-18`;

    await render(hbs`{{page-footer version=version lastUpdatedDate=lastUpdatedDate}}`);

    assert.ok(find('.footer'));
    assert.equal(find('.footer .app-version').textContent.trim(), '1.1.1', 'it has the correct version');
    assert.equal(find('.footer .app-updated-date').textContent.trim(), '2016-10-18', 'it has the correct date');
    assert.equal(find('.footer').textContent.trim(), expectedWording, 'it hast he correct wording');
  });
});
