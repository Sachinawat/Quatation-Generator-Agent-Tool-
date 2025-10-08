document.addEventListener('DOMContentLoaded', () => {
    const addItemBtn = document.getElementById('add-item');
    const addTermBtn = document.getElementById('add-term');
    const itemsContainer = document.getElementById('items-container');
    const termsContainer = document.getElementById('terms-container');
    const generatePdfBtn = document.getElementById('generate-pdf');

    addItemBtn.addEventListener('click', () => {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('item');
        itemDiv.innerHTML = `
            <input type="text" placeholder="Item Description">
            <input type="number" placeholder="Quantity">
            <input type="number" placeholder="Unit Price">
            <button class="remove-item">Remove</button>
        `;
        itemsContainer.appendChild(itemDiv);
        attachRemoveListener(itemDiv, 'remove-item');
    });

    addTermBtn.addEventListener('click', () => {
        const termDiv = document.createElement('div');
        termDiv.classList.add('term');
        termDiv.innerHTML = `
            <input type="text" placeholder="Term">
            <button class="remove-term">Remove</button>
        `;
        termsContainer.appendChild(termDiv);
        attachRemoveListener(termDiv, 'remove-term');
    });

    function attachRemoveListener(element, buttonClass) {
        const removeBtn = element.querySelector(`.${buttonClass}`);
        removeBtn.addEventListener('click', () => {
            element.remove();
        });
    }

    generatePdfBtn.addEventListener('click', () => {
        const quoteData = {
            company: {
                name: document.getElementById('company-name').value,
                address: document.getElementById('company-address').value,
                logo: document.getElementById('company-logo').files[0]
            },
            customer: {
                name: document.getElementById('customer-name').value,
                address: document.getElementById('customer-address').value
            },
            quote: {
                id: document.getElementById('quote-id').value,
                validationDate: document.getElementById('validation-date').value
            },
            items: [],
            terms: [],
            template: document.getElementById('template-select').value
        };

        // Get items
        const itemElements = itemsContainer.querySelectorAll('.item');
        itemElements.forEach(item => {
            const inputs = item.querySelectorAll('input');
            quoteData.items.push({
                description: inputs[0].value,
                quantity: inputs[1].value,
                unitPrice: inputs[2].value
            });
        });

        // Get terms
        const termElements = termsContainer.querySelectorAll('.term');
        termElements.forEach(term => {
            const input = term.querySelector('input');
            quoteData.terms.push(input.value);
        });

        fetch('http://127.0.0.1:5000/generate-quote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(quoteData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert('PDF generation started! Check the output folder.');
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while generating the PDF.');
        });
    });
});