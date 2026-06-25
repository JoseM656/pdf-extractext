# Importante

*Cada computadora debe tener certificados independientes*. Descargue `mkcert` y ejecute lo siguiente:

```bash
cd .infra/certs
mkcert "pdfmanager.local" "*.pdfmanager.local"
mv pdfmanager.local+1.pem pdfmanager.pem
mv pdfmanager.local+1-key.pem pdfmanager-key.pem
```
