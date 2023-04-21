from decouple import config

from ammo import AmmoDealsBot


def main():
    caliber = input("Enter a caliber: ")
    casing = input("Enter a casing: ")
    bullet_weight = input("Enter a weight: ")
    if caliber == "9mm":
        palmetto_url = config("PALMETTO_9MM_URL")
        warehouse_2a_url = config("WAREHOUSE_2A_9MM_URL")
        targets_sports_ammo_url = config("TARGET_SPORTS_AMMO_9MM_URL")
    elif caliber == "556":
        palmetto_url = config("PALMETTO_556_URL")
        targets_sports_ammo_url = config("TARGET_SPORTS_AMMO_556_URL")
    lucky_gunner_url = config("LUCKY_GUNNER_URL")
    ammunition_depot_url = config("AMMUNITION_DEPOT_URL")
    urls = [
        targets_sports_ammo_url,
        palmetto_url,
        # warehouse_2a_url,
        ammunition_depot_url,
        lucky_gunner_url,
    ]
    ammo_bot = AmmoDealsBot(caliber, casing, bullet_weight, urls)
    ammo_bot.run()


if __name__ == "__main__":
    main()
