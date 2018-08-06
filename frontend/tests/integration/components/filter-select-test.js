import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, click } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | filter select', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    this.set('name', 'filter_name');
    this.set('data', [
      { text: 'Choice #1' },
      { text: 'Choice #2' },
      { text: 'Choice #3' },
      { text: 'Choice #4' },
      { text: 'Choice #5' }
    ]);
    this.set('labelPath', 'text');
    this.set('value', 'fname');
    this.set('label', 'Filter Name');
    this.set('popover', 'This is the pop over text');

    await render(
      hbs`{{filter-select name=name data=data labelPath=labelPath value=value label=label popover=popover}}`
    );

    assert.ok(find('.filter.form-group'), 'it has the right root element');
    assert.equal(find('.filter label').textContent.trim(), 'Filter Name', 'it has the right label');
    assert.ok(find('.filter label .da-popover'), 'it has the popover trigger');
    assert.notOk(find('.popover'), 'the popover is not shown')

    await click('.filter .da-popover');
    // assert.ok(find('.popover'), 'it shows the popover')
    // assert.equal(find('.popover').textContent.trim(), 'This is the pop over text', 'the popover has the right text');
  });
});
