// Function to open the payment form modal
function openPaymentForm(paymentOption) {
  var modal = document.getElementById('paymentFormModal');
  modal.style.display = 'block';
}

// Function to open the payment modal
function openPaymentModal(speed, duration, price) {
    // Display the payment modal
    const modal = document.getElementById("paymentModal");
    modal.style.display = "block";
  
    // modal content with speed, duration, and price
    const modalContent = modal.querySelector(".modal-content");
    modalContent.innerHTML = `
      <span class="close" onclick="closePaymentModal()">&times;</span>
        <h2>Payment Options for ${speed} (${duration})</h2>
        <p>Price: &#8358;${price}</p>
        <div class="payment-option">
          <button onclick="openPaymentForm('Debit Card')">Debit Card</button>
        </div>
        <div class="payment-option">
          <button onclick="openPaymentForm('Bank Transfer')">Bank Transfer</button>
        </div>
        <div class="payment-option">
          <button onclick="openPaymentForm('USSD')">USSD</button>
        </div>
      `;
      document.getElementById("amount").value = price;
  }
  
  // close the payment modal
  function closePaymentModal() {
    const modal = document.getElementById("paymentModal");
    modal.style.display = "none";
  }

  // close the payment form modal
  function closePaymentFormModal() {
    var modal = document.getElementById('paymentFormModal');
    modal.style.display = 'none';
    resetPaymentForm();
    closePaymentModal();
  }
  
  // handle the selected payment method
  function makePayment(method) {
    // You can implement payment processing logic here
    alert(`Payment method selected: ${method}`);
    closePaymentModal();
  }

function setCookie(name, value, expirationDays) {
  const date = new Date();
  date.setTime(date.getTime() + (expirationDays * 24 * 60 * 60 * 1000));
  const expires = `expires=${date.toUTCString()}`;

  // Combining all attributes in the cookie string
  document.cookie = `${name}=${encodeURIComponent(value)}; ${expires}; path=/; SameSite=None; Secure`;
}

document.querySelectorAll('.btn').forEach(function(button) {
  button.addEventListener('click', function() {
      var package = this.getAttribute('data-package');
      var duration = this.getAttribute('data-duration');
      var price = this.getAttribute('price');

      

      // Storing data in sessionStorage
      sessionStorage.setItem('selectedPackage', package);
      sessionStorage.setItem('selectedDuration', duration);
      sessionStorage.setItem('selectedPrice', price);

      
      // Sending data to Flask app using AJAX
      fetch('/verify_transaction', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              package: package,
              duration: duration,
              price: price
          })
      })
      // .then(function(response) {
      //     // Handle response here (e.g., display a success message)
      // })
      .catch(function(error) {
          console.error('Error:', error);
      });
  });
});


