# Etsyv3 
## What it is

Python 3 client for the [Etsy Open API v3](https://developer.etsy.com/documentation/reference).

## How do I use it?

### Authentication

The authorisation flow in v3 of Etsy's API is somewhat different to the flow used in v2. It is the [OAuth 2.0 Authorization Code Grant](https://www.rfc-editor.org/rfc/rfc6749#section-4.1) flow, [documented quite well by Etsy themselves](https://developer.etsy.com/documentation/essentials/authentication/). Make sure you've done the setup at `Requesting an OAuth Token`, in terms of getting your Etsy API keystring and callback URLs set up.

In the `etsyv3.utils.util.auth` package, the `auth_helper.py` module contains a helper class (`AuthHelper`) for the authentication flow. Provided with the keystring, one of the redirect URLs that you've specific in your Etsy app setup, a list of scopes to be provided in this authentication (a list of strings at present, but likely to become a set of `enums` in future), a code verifier string (specified by you) and a state string (also specified by you), it will allow for some simplification of the process.

With your initialised `AuthHelper`, the flow looks something like this:

1) Call `get_auth_code()` on your `AuthHelper` - this will return an Etsy authentication URL
2) Go to that URL and authenticate with Etsy
3) Use the `state` and `code` params from the callback that Etsy will make to call `set_authorization_code(code, state)` on an `AuthHelper` object initialised with the same the arguments passed to your first one (this callback is likely to be in a completely new request context to the first - your original object may well no longer exist)
4) You can then call `get_access_token()` on your `AuthHelper` object and you should get a dictionary returned with the keys `access_token`, `refresh_token` and `expires_at`. These a required to create the `EtsyAPI` object.

#### Do I actually need a webapp to finish the authentication flow?

Technically no. If you set the callback URL to a localhost address that doesn't have an application listening on it, you can just copy and paste the `state` and `code` URL parameters that will be present in the 404'd URL that Etsy will redirect you to and then continue in calling `set_authorization_code()` and `get_access_token()` on the `AuthHelper` object.

Just set up something simple in Flask would be my recommendation if you're doing this for anything even semi-serious: it'll make your life easier.

In a Djano context, it could be as simple as something like the below, wired up to the router appropriately:

```python

def oauth_callback(request):
    state = request.GET["state"]
    code = request.GET["code"]
    auth = AuthHelper(
        keystring, redirect_uri, code_verifier="super_secret_and_random_code_verifier_string", state="super_secret_and_random_code_state_string"
    )
    auth.set_authorisation_code(code, state)
    token = auth.get_access_token()
    save_this_for_later(token)
    return HttpResponse("Logged in!")

```

### I'm authenticated, now what?

Now that you have your keystring, access token, refresh token and token expiry time, you can create your `EtsyAPI` object! The `EtsyAPI` initialiser requires a `keystring`, `token`, `refresh_token` and `expiry` (as a `datetime` object) to be set: these will be the values returned from the call to `get_access_token()` in authentication. A function can be specified as a named argument `refresh_save`, that takes three parameters `access_token`, `refresh_token` and `expires_at`. This function will be run whenever the token needs to be refreshed to update it for future use and store it somewhere.

You can call any of the Etsy API methods from the `EtsyAPI` object: they'll generally be just a snake-case form of the Etsy published names (eg `GetBuyerTaxonomyNodes` becomes `get_buyer_taxonomy_nodes()`).

For `POST` and `PUT` requests (requests that need payloads), there are subclassed `Request` types for each type. They generally take all required arguments into a constructor that is then serialised into JSON when passed to an API-calling method. Where you wish to null an optional parameter in a call, you should create the request parameter with the empty-form of whatever you're trying to null, so if the API takes a string, provide `""`; if a list, `[]`.

If you're using an IDE or a featureful text editor, your autocomplete should do you quite well in working out what you can do: I've made a point to use type hints for all method parameters, so it should be OK. I will be adding more docstrings over time, so it should hopefully get easier to use.

### How does `refresh_save` work?

It's intended to be a 'neat' way to handle refreshes - it's a function (or method) that takes the token and metadata and does *stuff* with it, whatever you want that stuff to be. It could look something like this:

```python

def refresh_save(access_token, refresh_token, expires_at):
    api_creds = get_some_persistence_object()
    api_creds.access_token = access_token
    api_creds.refresh_token = refresh_token
    api_creds.expires_at = expires_at
    api_creds.save()
    
```

## Implementation details


| **Etsy API**                                        | **Implemented**             |
|-----------------------------------------------------|-----------------------------|
| GetBuyerTaxonomyNodes                               | ✔️                          |
| GetPropertiesByBuyerTaxonomyId                      | ✔️                          |
| GetSellerTaxonomyNodes                              | ✔️                          |
| GetPropertiesByTaxonomyId                           | ✔️                          |
| CreateDraftListing                                  | ✔️                          |
| GetListingsByShop                                   | ✔️                          |
| DeleteListing                                       | ✔️                          |
| GetListing                                          | ✔️                          |
| FindAllListingsActive                               | ✔️                          |
| FindAllActiveListingsByShop                         | ✔️                          |
| GetListingsByListingIds                             | ✔️                          |
| GetFeaturedListingsByShop                           | ✔️                          |
| DeleteListingProperty                               | ✔️                          |
| UpdateListingProperty                               | ❌                           |
| GetListingProperty                                  | ❌ (501 only from Etsy)      |
| GetListingProperties                                | ✔️                          |
| UpdateListing                                       | ❌                           |
| GetListingsByShopReceipt                            | ✔️                          |
| GetListingsByShopSectionId                          | ✔️                          |
| DeleteListingFile                                   | ✔️                          |
| GetListingFile                                      | ✔️                          |
| GetAllListingFiles                                  | ✔️                          |
| UploadListingFile                                   | ❌                           |
| DeleteListingImage                                  | ✔️                          |
| GetListingImage                                     | ✔️                          |
| GetListingImages                                    | ✔️                          |
| UploadListingImage                                  | ❌                           |
| GetListingInventory                                 | ✔️                          |
| UpdateListingInventory                              | ✔️                          |
| GetListingOffering                                  | ✔️                          |
| GetListingProduct                                   | ✔️                          |
| CreateListingTranslation                            | ❌                           |
| GetListingTranslation                               | ✔️                          |
| UpdateListingTranslation                            | ❌                           |
| GetListingVariationImages                           | ✔️                          |
| UpdateVariationImages                               | ✔️                          |
| Ping                                                | ✔️                          |
| TokenScopes                                         | ✔️                          |
| GetShopPaymentAccountLedgerEntry                    | ✔️                          |
| GetShopPaymentAccountLedgerEntries                  | ✔️                          |
| GetPaymentAccountLedgerEntryPayments                | ✔️                          |
| GetShopPaymentByReceiptId                           | ✔️                          |
| GetPayments                                         | ✔️                          |
| GetShopReceipt                                      | ✔️ ️                        |
| UpdateShopReceipt                                   | ❌️ ️                        |
| GetShopReceipts                                     | ✔️ ️                        |
| CreateReceiptShipment                               | ❌                           |
| GetShopReceiptTransactionsByListing                 | ✔️                          |
| GetShopReceiptTransactionsByReceipt                 | ✔️                          |
| GetShopReceiptTransaction                           | ✔️                          |
| GetShopReceiptTransactionsByShop                    | ✔️                          |
| GetReviewsByListing                                 | ✔️                          |
| GetReviewsByShop                                    | ✔️                          |
| GetShippingCarriers                                 | ✔️                          |
| CreateShopShippingProfile                           | ❌                           |
| GetShopShippingProfiles                             | ✔️                          |
| DeleteShopShippingProfile                           | ✔️                          |
| GetShopShippingProfile                              | ✔️                          |
| UpdateShopShippingProfile                           | ❌                           |
| CreateShopShippingProfileDestination                | ❌                           |
| GetShopShippingProfileDestinationsByShippingProfile | ✔️                          |
| DeleteShopShippingProfileDestination                | ✔️                          |
| UpdateShopShippingProfileDestination                | ❌                           |
| CreateShopShippingProfileUpgrade                    | ❌                           |
| GetShopShippingProfileUpgrades                      | ✔️                          |
| DeleteShopShippingProfileUpgrade                    | ✔️                          |
| UpdateShopShippingProfileUpgrade                    | ❌                           |
| GetShop                                             | ✔️                          |
| UpdateShop                                          | ❌                           |
| GetShopByOwnerUserId                                | ✔️                          |
| FindShops                                           | ✔️                          |
| GetShopProductionPartners                           | ✔️                          |
| CreateShopSection                                   | ❌                           |
| GetShopSections                                     | ✔️                          |
| DeleteShopSection                                   | ✔️                          |
| GetShopSection                                      | ✔️                          |
| UpdateShopSection                                   | ❌                           |
| GetUser                                             | ✔️ ️                        |
| DeleteUserAddress                                   | ❌                           |
| GetUserAddress                                      | ❌ (Etsy only returns a 501) |
| GetUserAddresses                                    | ✔️                          |




