from VNP.packages.web_scraping import *

if __name__ == '__main__':
    snapshot_url = "https://clevershop.mk/product-category/mobilni-laptopi-i-tableti/"

    try:
        soup = get_soup(snapshot_url)
    except Exception as e:
        print(e)
        exit(1)

    page_numbers = soup.select(".page-numbers li")
    max_pages = int(page_numbers[-2].text)
    num_pages = [i for i in range(1, max_pages + 1)]

    products_page_url = "https://clevershop.mk/product-category/mobilni-laptopi-i-tableti/page/"
    products = []
    for page_number in num_pages:
        fetch_url = products_page_url + str(page_number) + "/"
        try:
            page_soup = get_soup(fetch_url)
        except Exception as e:
            continue

        product_elements = page_soup.select(".product-wrapper")
        for product_element in product_elements:
            title = product_element.select_one(".wd-entities-title").select_one("a").text
            children = list(product_element.select_one(".price").children)

            if len(children) == 1:
                regular_price = children[0].text
                discounted_price = "0 ден"
            else:
                regular_price = product_element.select(".woocommerce-Price-amount")[0].select_one("bdi").text
                discounted_price = product_element.select(".woocommerce-Price-amount")[1].select_one("bdi").text

            regular_price = format_white_space(regular_price)
            discounted_price = format_white_space(discounted_price)

            product_link = product_element.select_one(".product-image-link").get("href")
            query_string = product_element.select_one(".add_to_cart_button").get("href")
            if query_string.startswith("?"):
                add_to_cart_link = fetch_url + query_string
            else:
                add_to_cart_link = None
            product = {"title": title, "price": regular_price, "discounted_price": discounted_price,
                       "link": product_link, "add_to_cart": add_to_cart_link}
            products.append(product)

        print_elements(products)
    df = pd.DataFrame(products)
    # print(df.to_string())

    df.to_csv("./products.csv", index=False)
