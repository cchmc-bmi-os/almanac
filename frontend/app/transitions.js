export default function() {
  this.transition(
    this.hasClass('cde-detail'),
    this.toValue(true),
    this.use('toDown'),
    this.reverse('toUp')
  );

  this.transition(
    this.fromRoute('cde-view.index'),
    this.fromRoute('cde-view.info'),
    this.fromRoute('cde-view.codes'),
    this.fromRoute('cde-view.visibility'),
    this.use('toLeft')
  );

  this.transition(
    this.fromRoute('cde-view'),
    this.toRoute('cde-version'),
    this.use('toUp'),
    this.reverse('toDown')
  );
}
