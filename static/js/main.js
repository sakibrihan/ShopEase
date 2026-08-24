/* ============================================
   ShopEase — Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

    // ---- Mobile Nav Toggle ----
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('active');
        });
    }

    // ---- Auto-dismiss alerts after 5 seconds ----
    document.querySelectorAll('.alert').forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function () { alert.remove(); }, 300);
        }, 5000);
    });

    // ---- Quantity Controls (Product Detail) ----
    const qtyInput = document.getElementById('qtyInput');
    const qtyMinus = document.getElementById('qtyMinus');
    const qtyPlus = document.getElementById('qtyPlus');
    const maxStock = qtyInput ? parseInt(qtyInput.getAttribute('max')) || 99 : 99;

    if (qtyMinus && qtyInput) {
        qtyMinus.addEventListener('click', function () {
            let val = parseInt(qtyInput.value) || 1;
            if (val > 1) { qtyInput.value = val - 1; }
        });
    }
    if (qtyPlus && qtyInput) {
        qtyPlus.addEventListener('click', function () {
            let val = parseInt(qtyInput.value) || 1;
            if (val < maxStock) { qtyInput.value = val + 1; }
        });
    }
    if (qtyInput) {
        qtyInput.addEventListener('change', function () {
            let val = parseInt(this.value) || 1;
            if (val < 1) val = 1;
            if (val > maxStock) val = maxStock;
            this.value = val;
        });
    }

    // ---- Payment Method Tabs ----
    const paymentMethods = document.querySelectorAll('.payment-method');
    paymentMethods.forEach(function (method) {
        const radio = method.querySelector('input[type="radio"]');
        if (radio) {
            radio.addEventListener('change', function () {
                paymentMethods.forEach(function (m) { m.classList.remove('active'); });
                method.classList.add('active');
            });
            // Set initial active
            if (radio.checked) method.classList.add('active');
        }
    });

    // ---- Payment Form Validation ----
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function (e) {
            const activeMethod = document.querySelector('input[name="payment_method"]:checked');
            if (!activeMethod) {
                e.preventDefault();
                alert('Please select a payment method.');
                return;
            }

            if (activeMethod.value === 'card') {
                const cardName = document.getElementById('cardName');
                const cardNumber = document.getElementById('cardNumber');
                const cardExpiry = document.getElementById('cardExpiry');
                const cardCvv = document.getElementById('cardCvv');

                if (!cardName.value || !cardNumber.value || !cardExpiry.value || !cardCvv.value) {
                    e.preventDefault();
                    alert('Please fill in all card details.');
                    return;
                }
            }

            if (activeMethod.value === 'upi') {
                const upiId = document.getElementById('upiId');
                if (!upiId.value) {
                    e.preventDefault();
                    alert('Please enter your UPI ID.');
                    return;
                }
            }

            // Show loading
            const submitBtn = paymentForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '⏳ Processing Payment...';
            }
        });
    }

    // ---- Card Number Formatting ----
    const cardNumberInput = document.getElementById('cardNumber');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function () {
            let val = this.value.replace(/\D/g, '').substring(0, 16);
            let formatted = val.replace(/(\d{4})(?=\d)/g, '$1 ');
            this.value = formatted;
        });
    }

    // ---- OTP Input: Auto-focus and numbers only ----
    const otpInput = document.getElementById('id_otp');
    if (otpInput) {
        otpInput.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').substring(0, 6);
        });
    }
});
