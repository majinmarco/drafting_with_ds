/* Reusable retrieval-practice quiz.
   Usage: <div class="quiz" data-quiz></div> then call
   renderQuiz(el, { question, options: [..], answer: idx, explain: {good, bad} })
   or declare inline:
   <script> quizzes.push({ sel: '#q1', question, options, answer, explain }) </script>
   Options are shuffled on each render so position carries no signal. */

window.quizzes = window.quizzes || [];

function renderQuiz(el, spec) {
  const order = spec.options.map((_, i) => i);
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }

  el.innerHTML = '';
  const label = document.createElement('div');
  label.className = 'quiz-label';
  label.textContent = spec.label || 'Check yourself';
  const q = document.createElement('div');
  q.className = 'quiz-q';
  q.textContent = spec.question;
  const feedback = document.createElement('div');
  feedback.className = 'quiz-feedback';
  el.append(label, q);

  const buttons = order.map((origIdx) => {
    const b = document.createElement('button');
    b.className = 'quiz-opt';
    b.textContent = spec.options[origIdx];
    b.addEventListener('click', () => {
      buttons.forEach((btn) => (btn.disabled = true));
      const right = origIdx === spec.answer;
      b.classList.add(right ? 'correct' : 'wrong');
      if (!right) buttons[order.indexOf(spec.answer)].classList.add('correct');
      feedback.textContent = right ? '✓ ' + (spec.explain?.good || 'Correct.')
                                   : '✗ ' + (spec.explain?.bad || 'Not quite.');
      feedback.classList.add('show', right ? 'good' : 'bad');
    });
    el.appendChild(b);
    return b;
  });

  el.appendChild(feedback);
}

document.addEventListener('DOMContentLoaded', () => {
  window.quizzes.forEach((spec) => {
    const el = document.querySelector(spec.sel);
    if (el) renderQuiz(el, spec);
  });
});
