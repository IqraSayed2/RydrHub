document.addEventListener("DOMContentLoaded", function () {
  const pickupInput = document.getElementById("pickupDateTime");
  const returnInput = document.getElementById("returnDateTime");
  const totalSpan = document.getElementById("estimatedTotal");

  const dailyRate = parseFloat(totalSpan.dataset.dailyrate);

  if (isNaN(dailyRate)) {
    console.error(
      "Error: Daily rental rate (data-dailyrate) is not a valid number."
    );
  }

  function updateTotal() {
    if (!pickupInput.value || !returnInput.value) {
      totalSpan.textContent = "₹" + dailyRate.toFixed(2);
      return;
    }

    const pickup = new Date(pickupInput.value);
    const ret = new Date(returnInput.value);

    if (isNaN(pickup.getTime()) || isNaN(ret.getTime()) || ret <= pickup) {
      totalSpan.textContent = "₹" + dailyRate.toFixed(2);
      return;
    }

    let diffTime = ret - pickup;
    let diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    totalSpan.textContent = "₹" + (diffDays * dailyRate).toFixed(2);
  }

  pickupInput.addEventListener("change", updateTotal);
  returnInput.addEventListener("change", updateTotal);

  if (pickupInput.value && returnInput.value) {
    updateTotal();
  } else {
    totalSpan.textContent = "₹" + dailyRate.toFixed(2);
  }
});

//----------------------------

document.addEventListener("DOMContentLoaded", () => {
  const faqButtons = document.querySelectorAll(".faq-question-button");

  faqButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const isExpanded = button.getAttribute("aria-expanded") === "true";
      const answer = button.nextElementSibling; // The answer content div

      // Close all other open FAQs
      faqButtons.forEach((otherButton) => {
        if (
          otherButton !== button &&
          otherButton.getAttribute("aria-expanded") === "true"
        ) {
          otherButton.setAttribute("aria-expanded", "false");
          otherButton.nextElementSibling.style.maxHeight = null;
          otherButton.querySelector(".faq-arrow").style.transform =
            "rotate(0deg)";
        }
      });

      // Toggle current FAQ
      button.setAttribute("aria-expanded", !isExpanded);
      if (isExpanded) {
        answer.style.maxHeight = null;
        button.querySelector(".faq-arrow").style.transform = "rotate(0deg)";
      } else {
        answer.style.maxHeight = answer.scrollHeight + "px"; // Set to actual height
        button.querySelector(".faq-arrow").style.transform = "rotate(180deg)";
      }
    });
  });
});
