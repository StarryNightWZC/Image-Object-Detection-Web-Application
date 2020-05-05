import os
from website import app


if __name__=="__main__":
  #  app.run(debug=True, use_reloder=False)
  #app.secret_key = "super secret key"
  app.run(port=5001,debug=True)