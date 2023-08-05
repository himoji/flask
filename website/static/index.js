function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/question";
  });
}

function answerYes(noteId) {
  fetch("/answer-question", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId , noteAnswer: "yes"}),
  }).then((_res) => {
    
    window.location.href = "/bonus";
  });
}

function answerNo(noteId) {
  fetch("/answer-question", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId , noteAnswer: "no"}),
  }).then((_res) => {
    window.location.href = "/bonus";
  });
}