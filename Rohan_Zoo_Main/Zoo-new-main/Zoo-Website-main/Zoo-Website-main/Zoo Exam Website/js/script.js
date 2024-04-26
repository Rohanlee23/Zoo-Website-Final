// Define ticket prices
const adultTicketPrice = 20; // Price for one adult ticket
const childTicketPrice = 10; // Price for one child ticket

// Function to calculate total ticket price
function calculateTotalTicketsPrice(numAdults, numChildren) {
    const totalAdultPrice = numAdults * adultTicketPrice;
    const totalChildPrice = numChildren * childTicketPrice;
    return totalAdultPrice + totalChildPrice;
}

// Function to handle purchase
function purchaseTickets(numAdults, numChildren) {
    const totalPrice = calculateTotalTicketsPrice(numAdults, numChildren);
    console.log("Total Price: $" + totalPrice);
    // Here you can add further logic for payment processing or other actions
}

// Example usage
const numAdults = 2; // Number of adult tickets
const numChildren = 3; // Number of child tickets
purchaseTickets(numAdults, numChildren);