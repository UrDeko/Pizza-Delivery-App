import paypalrestsdk


class PayPalPayment():

    @staticmethod
    def create_payment(total_price, unpaid_order_id):

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": f"{total_price:.2f}",
                    "currency": "USD"
            },
            "description": "Order from Pizza Club"}],
            "redirect_urls": {
                "return_url": f"http://127.0.0.1:5000/payment/execute?unpaid_order_id={unpaid_order_id}",
                "cancel_url": f"http://127.0.0.1:5000/payment/cancel?unpaid_order_id={unpaid_order_id}"
            }
        })

        return payment
    
    def find_payment(payment_id):

        return paypalrestsdk.Payment.find(payment_id)