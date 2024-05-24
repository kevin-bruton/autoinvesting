
deploy:
	$(info *************************** )
	$(info ***** UPDATING SERVER ***** )
	$(info *************************** )
	git pull
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
cron:
	$(info ************************* )
	$(info ********* CRON ********** )
	$(info ************************* )
	python cron.py
api:
	$(info ************************* )
	$(info ******* FASTAPI ********* )
	$(info ************************* )
	python run_fastapi.py
