# Etsyv3 
## What it is

Python 3 client for the [Etsy Open API v3](https://developer.etsy.com/documentation/reference).

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




