"use strict";


/* -------------------------------------------------------
   Helpers
------------------------------------------------------- */

const $ = (id) => document.getElementById(id);


async function request(url, options = {}) {

    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        },
        ...options
    });

    const data =
        await response
            .json()
            .catch(() => ({}));

    if (!response.ok) {

        throw new Error(
            data.error ||
            data.detail ||
            `Request failed (${response.status})`
        );
    }

    return data;
}


function setLoading(button, loading) {

    if (!button) {
        return;
    }

    if (!button.dataset.label) {
        button.dataset.label =
            button.textContent;
    }

    button.disabled = loading;

    button.textContent =
        loading
            ? "Working..."
            : button.dataset.label;
}


function showText(element, text) {

    element.textContent = text;

    element.className = "output";
}


function showError(element, error) {

    element.textContent =
        error.message ||
        "Something went wrong.";

    element.className =
        "output error";
}


function escapeHtml(value) {

    return String(value).replace(
        /[&<>"']/g,
        (character) => {

            const map = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            };

            return map[character];
        }
    );
}


function setStatus(message) {

    const status = $("status");

    if (status) {
        status.textContent = message;
    }
}


/* -------------------------------------------------------
   Save original button labels
------------------------------------------------------- */

document
    .querySelectorAll("button")
    .forEach((button) => {

        button.dataset.label =
            button.textContent.trim();

    });


/* -------------------------------------------------------
   Q&A
------------------------------------------------------- */

$("qaForm").addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        const button =
            event.submitter;

        const output =
            $("qaResult");

        const question =
            $("question").value.trim();

        if (!question) {
            return;
        }

        setLoading(button, true);

        setStatus(
            "EduGenie is thinking..."
        );

        try {

            const data =
                await request(
                    `/qna?question=${encodeURIComponent(question)}`
                );

            showText(
                output,
                data.answer
            );

            setStatus(
                "Answer generated successfully."
            );

        } catch (error) {

            showError(
                output,
                error
            );

            setStatus(
                "Could not generate the answer."
            );

        } finally {

            setLoading(button, false);
        }
    }
);


/* -------------------------------------------------------
   Explanation
------------------------------------------------------- */

$("explainForm").addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        const button =
            event.submitter;

        const output =
            $("explanationResult");

        const topic =
            $("topic").value.trim();

        if (!topic) {
            return;
        }

        setLoading(button, true);

        setStatus(
            "Preparing explanation..."
        );

        try {

            const data =
                await request(
                    "/explain",
                    {
                        method: "POST",

                        body: JSON.stringify({
                            topic
                        })
                    }
                );

            showText(
                output,
                data.explanation
            );

            setStatus(
                "Explanation generated successfully."
            );

        } catch (error) {

            showError(
                output,
                error
            );

            setStatus(
                "Could not generate explanation."
            );

        } finally {

            setLoading(button, false);
        }
    }
);


/* -------------------------------------------------------
   Summary
------------------------------------------------------- */

$("summaryForm").addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        const button =
            event.submitter;

        const output =
            $("summaryResult");

        const text =
            $("summaryText").value.trim();

        if (!text) {
            return;
        }

        setLoading(button, true);

        setStatus(
            "Summarizing your text..."
        );

        try {

            const data =
                await request(
                    "/summarize",
                    {
                        method: "POST",

                        body: JSON.stringify({
                            text
                        })
                    }
                );

            showText(
                output,
                data.summary
            );

            setStatus(
                "Summary generated successfully."
            );

        } catch (error) {

            showError(
                output,
                error
            );

            setStatus(
                "Could not generate summary."
            );

        } finally {

            setLoading(button, false);
        }
    }
);


/* -------------------------------------------------------
   Quiz
------------------------------------------------------- */

let latestQuiz = [];


$("quizForm").addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        const button =
            event.submitter;

        const output =
            $("quizResult");

        const answerButton =
            $("showAnswersButton");

        const text =
            $("quizText").value.trim();

        if (!text) {
            return;
        }

        setLoading(button, true);

        setStatus(
            "Generating your quiz..."
        );

        try {

            const data =
                await request(
                    "/quiz",
                    {
                        method: "POST",

                        body: JSON.stringify({
                            text
                        })
                    }
                );

            latestQuiz =
                data.quiz || [];

            output.innerHTML =
                latestQuiz
                    .map(
                        (quiz, index) => {

                            const options =
                                quiz.options
                                    .map(
                                        (option, optionIndex) => {

                                            return `
                                                <label class="option">

                                                    <input
                                                        type="radio"
                                                        name="quiz-${index}"
                                                        value="${escapeHtml(option)}"
                                                    >

                                                    <span>
                                                        ${String.fromCharCode(65 + optionIndex)}.
                                                        ${escapeHtml(option)}
                                                    </span>

                                                </label>
                                            `;
                                        }
                                    )
                                    .join("");

                            return `
                                <div class="quiz-question">

                                    <div class="quiz-title">
                                        Q${index + 1}.
                                        ${escapeHtml(quiz.question)}
                                    </div>

                                    ${options}

                                    <div class="correct-answer">
                                        Correct Answer:
                                        ${escapeHtml(quiz.answer)}
                                    </div>

                                </div>
                            `;
                        }
                    )
                    .join("");

            output.className =
                "output";

            answerButton.classList.remove(
                "hidden"
            );

            answerButton.dataset.visible =
                "false";

            answerButton.textContent =
                "Show Answers";

            setStatus(
                "Quiz generated successfully."
            );

        } catch (error) {

            showError(
                output,
                error
            );

            answerButton.classList.add(
                "hidden"
            );

            setStatus(
                "Could not generate quiz."
            );

        } finally {

            setLoading(button, false);
        }
    }
);


/* -------------------------------------------------------
   Show Answers
------------------------------------------------------- */

$("showAnswersButton").addEventListener(
    "click",
    () => {

        const output =
            $("quizResult");

        const visible =
            output.classList.contains(
                "answers-visible"
            );

        if (visible) {

            output.classList.remove(
                "answers-visible"
            );

            $("showAnswersButton").textContent =
                "Show Answers";

        } else {

            output.classList.add(
                "answers-visible"
            );

            $("showAnswersButton").textContent =
                "Hide Answers";
        }
    }
);


/* -------------------------------------------------------
   Learning Recommendations
------------------------------------------------------- */

$("learningForm").addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        const button =
            event.submitter;

        const output =
            $("learningResult");

        const topic =
            $("learningTopic")
                .value
                .trim();

        if (!topic) {
            return;
        }

        setLoading(button, true);

        setStatus(
            "Building your learning path..."
        );

        try {

            const data =
                await request(
                    `/learn/recommendations?topic=${encodeURIComponent(topic)}`
                );

            showText(
                output,
                `Learning Recommendations for "${data.topic}"\n\n${data.recommendation}`
            );

            setStatus(
                "Learning recommendations generated successfully."
            );

        } catch (error) {

            showError(
                output,
                error
            );

            setStatus(
                "Could not generate recommendations."
            );

        } finally {

            setLoading(button, false);
        }
    }
);