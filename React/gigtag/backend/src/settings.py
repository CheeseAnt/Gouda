import os
import dotenv

dotenv.load_dotenv('.env')

TICKETMASTER_API_KEY = os.environ.get('TICKETMASTER_API_KEY')
