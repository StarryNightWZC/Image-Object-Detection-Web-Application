from website import db
from website import app
from website.RequestPerMinute import RequestPerMinute
from pytz import timezone
from datetime import datetime

def record_requests(instance_id):
    try:
        requests = RequestPerMinute(instance_id=instance_id,
                                    timestamp=datetime.now(timezone(app.config['ZONE'])))
        db.session.add(requests)
        db.session.commit()
    except Exception as e:
        print(e)
