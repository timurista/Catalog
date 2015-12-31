# initializes db with items


# TODO MAKE ITEMS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, CatalogItem, User
 
engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# dropping values and recreating
session.query(Category).delete()
session.query(CatalogItem).delete()
session.query(User).delete()

# for User information
user1 = User(name="User 1 - Luke", email="skywalkerules@gmail.com", picture="images/luke_profile.jpg")
session.add(user1)
session.commit()

user2 = User(name="User 2- Vader", email="darksideiscallingyou@gmail.com", picture="images/vader_profile.jpg")
session.add(user2)
session.commit()

#for Soccer Category
category1 = Category(name = "Soccer", user=user1)
print category1.user

session.add(category1)
session.commit()

catalogItem2 = CatalogItem(name = "Blue Durable Soccer Ball", title="Durable Soccer Ball That Gives Back: One World Futbol (Sizes 4 & 5 Available)", description = "The ultra-durable ball that plays on and on--anywhere and everywhere. The One World Futbol never needs a pump and never goes flat, even when punctured, eliminating pumps and needles and the waste of worn-out balls. A single One World Futbol can withstand the toughest environments in the world and lasts for years without maintenance. The One World Futbol is designed with lesser bounce for hard surfaces like streets, rocky landscapes and dirt lots -but it plays great on sand and turf, too.", price = "$39.50", category = category1, img = "http://ecx.images-amazon.com/images/I/915m4UKodtL._SL1500_.jpg", user=user1)

session.add(catalogItem2)
session.commit()


catalogItem3 = CatalogItem(name = "Adidas Messi Soccer Shoe", title="Adidas Performance Men's Messi 15.3 FG/AG Soccer Shoe", description = "Adidas Soccer Shoe. Product Dimensions: 19 x 9 x 5 inches. Shipping Weight: 3 pounds (View shipping rates and policies)", price = "$57.88", category = category1, img = "http://ecx.images-amazon.com/images/I/81efc1bl6FL._UX695_.jpg", user=user1)

session.add(catalogItem3)
session.commit()

catalogItem4 = CatalogItem(name = "Adidas Shin Gaurd", title="adidas Performance Ghost Guard", description = "adidas Adult Ghost Shin Guards Dominate the Pitch with Durable Hard Shell Shin Guards! Fear no defender's cleat when you wear the tough, highly protective Ghost Shin Guards. Colorful shields that slip into the cushioned compression sleeves for a quick, easily adjustable fit. adidas Adult Ghost Shin Guards features: Designed to protect your from bruises or other injury during play Lightweight guards have a colorful hard shell and a soft, synthetic lining Easy slip on styling Compression sleeve gives players a secure fit Compression fit helps circulation and recovery Cushioned EVA backing Shell: 100%% Polypropylene injection molded Sleeve: 100%% Polyester Meets NOCSAE standard adidas Ghost Shin Guards...For Unrestricted Play!", price = "$19.99", category = category1, img = "http://ecx.images-amazon.com/images/I/71IAm78oKmL._SL1200_.jpg", user=user1)

session.add(catalogItem4)
session.commit()

# for weight lifting category
category2 = Category(name = "Weight Lifting", user=user2)

session.add(category2)
session.commit()

catalogItem2 = CatalogItem(name = "CAP Barbaell Standard Grip Plate", title="25 lb CAP Barbell Standard Grip Plate", description = "The CAP Barbell Standard Grip Plate comes in a variety of different weight levels to allow the user a customized workout. It has a machined center hole and a baked enamel finish. The 3-hole grip design allows for easy and safe handling and the plates accommodate 1-inch bars. The grip plate is ideal for cardio vascular fitness and strength training. About CAP Barbell CAP Barbell is a leading distributor and provider of fitness equipment. Launched in 1982 with a small inventory of free weights and benches, CAP Barbell has grown over the past 20+ years to include more than 600 products in 10 categories. Headquartered in Houston, Texas, CAP Barbell is dedicated to providing quality fitness equipment at competitive prices, by constructively designing, accurately testing, and manufacturing its products to perfection. Machined center hole and a baked enamel finish. 3-hole grip design allows for easy and safe handling. Choose from a variety of weight sizesAccommodates 1-inch bars.", price = "$19.25", category = category2, img = "http://ecx.images-amazon.com/images/I/81Fpe3PDwLL._SL1500_.jpg", user=user2)

session.add(catalogItem2)
session.commit()


catalogItem3 = CatalogItem(name = "Stormtrooper Star T Shirt Large Black", title="Stormtrooper Star Wars Men's T-Shirt Tee Shirt", description = 'Stormtrooper Star Wars Mens Tee Shirts.Tees are made from 100%% cotton and come in sizes S,M,L,XL . Mens T-Shirt Sizing Suggestions in lbs: SMALL - Under 150lbs. MEDIUM - 150-170lbs. LARGE - 170-195lbs. X-LARGE - 195-220lbs. XXLARGE - 220-260lbs. Note: Mens Tank Top sizing are only a suggestion. UNDERARM MEASUREMENT APPROX\': Small-38", Medium-40", Large-42", X-Large-44", XXLarge-46"+. LENGTH APPROX\': Small-28", Medium-29", Large-29", X-Large-30-31", XXLarge-30-31".', price = "$57.88", category = category2, img = "https://img1.etsystatic.com/072/1/9977709/il_340x270.803028951_h98r.jpg", user=user2)

session.add(catalogItem3)
session.commit()

catalogItem4 = CatalogItem(name = "PowerLine PPR200X Power Rack", title="PowerLine PPR200X Power Rack", description = "PowerLine Power Rack. Fire up your workouts on one of the first inventions that allowed weightlifters to workout safely and effectively, the Power Rack. Created several years ago, nearly every gym has one, so why not you? With the wide walk in design there is plenty of side to side movement for a variety of exercises such as squats, incline, decline, flat and military presses as well as shrugs and calf raises. Complete with 18 positions, two heat tempered lift offs and two saber style safety rods so you can keep your exercise routine the way it should be simple and effective. Shown with options Lat Attachment PLA200, Bench PFID130W. All barbells, weights and collars optional", price = "$529.99", category = category2, img = "http://ecx.images-amazon.com/images/I/51V47Lk5LpL._SY355_.jpg", user=user2)

session.add(catalogItem4)
session.commit()


# for running category
category3 = Category(name = "Running", user=user1)

session.add(category3)
session.commit()

catalogItem2 = CatalogItem(name = "Saucony Men Cohesion 8 Running Shoe", title="Saucony Men's Cohesion 8 Running Shoe", description = "Breathable mesh and synthetic uppers materials. External heel counter aids in stabilizing the heel. Reflective hits for added visibility in low lighting. Plush tongue and collar. Breathable fabric lining for a great in-shoe feel. Removable foam insole. IMEVA midsole provides increased shock attenuation, responsive cushioning and lasting durability. Saucony is among the most respected names in running shoes. We offer a wide range of running and walking shoes, each with the Saucony trademark fit, feel and performance. We've spent years studying the biomechanics of top athletes. Our goal? To develop creatively engineered systems that maximize your performance in your specific activity, allowing you to focus on the activity instead of the equipment. From our studies have come many innovative Saucony concepts. Advanced technologies-like Grid, the first sole-based stability and cushioning system--provide an advantage to athletes of all types.", price = "$69.99", category = category3, img = "http://ecx.images-amazon.com/images/I/81O72SuPW5L._UX575_.jpg", user=user1)

session.add(catalogItem2)
session.commit()


category4 = Category(name = "Basketball", user=user2)

session.add(category4)
session.commit()


catalogItem2 = CatalogItem(name = "Tachikara Colored Regulation Size BasketBall", title="Tachikara Colored Regulation Size BasketBall", description = "Tachikara SGB-7RC regulation size 2 color rubber basketball is perfect for clubs, camps and recreational use. Made with top grade rubber and nylon-yarn wound for durability. A colorful rubber basketball with a raised pebbled grip.", price = "$12.99", category = category4, img = "http://ecx.images-amazon.com/images/I/81zFJiL6BWL._SL1500_.jpg", user=user2)

session.add(catalogItem2)
session.commit()


print "added menu items!"
