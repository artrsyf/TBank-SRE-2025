DOMAIN = st-ab1-fadeev.ingress.sre-ab.ru

HELLO_APP_MANIFESTS = ./hello-app/
WHOAMI_APP_MANIFESTS = ./whoami-app/

deploy-hello:
	kubectl apply -f $(HELLO_APP_MANIFESTS)

deploy-whoami:
	kubectl apply -f $(WHOAMI_APP_MANIFESTS)

resources:
	kubectl get deploy,po,svc,ing,cm -o wide

test-hello:
	powershell -Command "Start-Sleep -Seconds 5"
	curl -v http://$(DOMAIN)/hello

test-whoami:
	powershell -Command "Start-Sleep -Seconds 5"
	curl -v http://$(DOMAIN)/whoami

clean:
	kubectl delete -f $(HELLO_APP_MANIFESTS)
	kubectl delete -f $(WHOAMI_APP_MANIFESTS)

run:
	$(MAKE) deploy-hello
	$(MAKE) deploy-whoami
	$(MAKE) resources
	$(MAKE) test-hello
	$(MAKE) test-whoami
	$(MAKE) clean

.PHONY: deploy-hello deploy-whoami resources test-hello test-whoami clean run
