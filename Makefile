deploy-front:
	$(info *************************** )
	$(info ***** DEPLOYING FRONT ***** )
	$(info *************************** )
	cd autoinvesting-ui && git pull
deploy-back:
	$(info ************************** )
	$(info ***** DEPLOYING BACK ***** )
	$(info ************************** )
	sudo systemctl stop waitress.service
	cd autoinvesting && git pull
	sudo systemctl start waitress.service
	sudo systemctl status waitress.service
deploy:	deploy-front deploy-back
update-from-mt:
	$(info ************************* )
	$(info *** UPDATING FROM MT  *** )
	$(info ************************* )
	cd autoinvesting && python update_from_mt.py
import-strategies:
	$(info ************************* )
	$(info *** IMPORTING STRATS  *** )
	$(info ************************* )
	cd autoinvesting && python import_strategies.py
trade-copier:
	$(info ************************* )
	$(info ***** TRADE COPIER ****** )
	$(info ************************* )
	cd autoinvesting && python trade_copier.py

