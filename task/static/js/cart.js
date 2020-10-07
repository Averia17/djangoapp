var updateBtns = document.getElementsByClassName('update-cart')


for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
		var size = GetSize(this.dataset.size)

		console.log('productId:', productId, 'Action:', action)
		console.log('USER:', user)
        console.log(size); //добавить try catch
		if (user == 'AnonymousUser'){
			addCookieItem(productId, action, size)
		}else{
			updateUserOrder(productId, action, size)
		}
	})
}

function GetSize(dataset_size) {
    try {
        if(dataset_size != undefined)
            return dataset_size;
        else {
            size = document.querySelector('input[name="selectedSize"]:checked').value;
            if (size == undefined)
                throw new Error('Выберите размер')
        }
        return size;
    }
    catch (e) {
        console.error('внешний блок catch', e.message);
    }

}
function updateUserOrder(productId, action, size){
	console.log('User is authenticated, sending data...')

		var url = '/update_item/'

		fetch(url, {
			method:'POST',
			headers:{
				'Content-Type':'application/json',
				'X-CSRFToken':csrftoken,
			},
			body:JSON.stringify({'productId':productId, 'action':action, 'size': size})
		})
		.then((response) => {
		   return response.json();
		})
		.then((data) => {
		    location.reload()
		});
}

function addCookieItem(productId, action, size){
	console.log('User is not authenticated')

	if (action == 'add'){
		if (cart[productId] == undefined){
		    cart[productId] = []
            cart[productId][0] = {'quantity':1, 'size': size}
		}
		else
		{
		    isSizeInArray = false
		    objectNum = 0
		    for(k = 0; k < cart[productId].length; k++) {
		        if(cart[productId][k]['size'] == size) {
		            isSizeInArray = true
		            objectNum = k
		        }
		    }
		    if(isSizeInArray){
		        cart[productId][objectNum]['quantity'] += 1
		    }
		    else {
		        cart[productId][cart[productId].length] = {'quantity':1, 'size': size}
		    }
	    }
	}
    if (action == 'remove') {
	    objectNum = 0
	    console.log(cart[productId].length);
        for(k = 0; k < cart[productId].length; k++) {
            if(cart[productId][k]['size'] == size)
            {
               objectNum = k
               break;
            }
        }
        cart[productId][objectNum]['quantity'] -= 1
        if (cart[productId][objectNum]['quantity'] <= 0)
        {
            console.log('Item should be deleted')
            cart[productId].splice(objectNum, 1)
           
        }

    }

	console.log('CART:', cart)
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"

	location.reload()
}
