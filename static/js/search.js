document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.getElementById('search-btn');
    const categorySelect = document.getElementById('category');
    const equipmentType = document.getElementById('equipment-type');
    const minPrice = document.getElementById('min-price');
    const maxPrice = document.getElementById('max-price');
    const listingsContainer = document.getElementById('listings-container');

    searchBtn.addEventListener('click', function() {
        const params = new URLSearchParams({
            category_id: categorySelect.value,
            equipment_type: equipmentType.value,
            min_price: minPrice.value,
            max_price: maxPrice.value
        });

        fetch(`/search?${params.toString()}`)
            .then(response => response.json())
            .then(listings => {
                listingsContainer.innerHTML = '';
                listings.forEach(listing => {
                    const listingHtml = `
                        <div class="col-md-4 mb-4">
                            <div class="card h-100">
                                <img src="${listing.image_url || '/static/images/placeholder.svg'}" 
                                     class="card-img-top" 
                                     alt="${listing.title}">
                                <div class="card-body">
                                    <h5 class="card-title">${listing.title}</h5>
                                    <p class="card-text">${listing.category} - ${listing.equipment_type}</p>
                                    <p class="card-text"><strong>$${listing.price.toFixed(2)}</strong></p>
                                    <a href="/listing/${listing.id}" class="btn btn-primary">View Details</a>
                                </div>
                            </div>
                        </div>
                    `;
                    listingsContainer.innerHTML += listingHtml;
                });
            })
            .catch(error => console.error('Error:', error));
    });
});
