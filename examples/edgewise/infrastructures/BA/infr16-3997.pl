bwTh(3).
hwTh(1).

node(n11, [js, python, ubuntu], (x86, 704), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n9, [python, ubuntu, gcc], (arm64, 576), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [cam12, heat]).
node(n2, [mySQL, js, gcc], (x86, 448), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [cam21]).
node(n12, [ubuntu, js, mySQL, python], (arm64, 800), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n10, [ubuntu, mySQL, python, js, gcc], (arm64, 384), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n0, [python, mySQL, gcc], (arm64, 736), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [piCamera2]).
node(n1, [ubuntu, mySQL, python, js, gcc], (arm64, 416), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n3, [python], (x86, 384), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [piCamera1]).
node(n5, [gcc, mySQL], (x86, 544), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [nutrient, cam22, water]).
node(n8, [js], (arm64, 544), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [cam11]).
node(n7, [ubuntu, python], (arm64, 448), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [energy, iphoneXS]).
node(n13, [python, ubuntu, mySQL, gcc], (arm64, 544), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n15, [ubuntu], (x86, 704), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n4, [python, ubuntu], (arm64, 704), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [soil, arViewer]).
node(n14, [gcc, js], (arm64, 576), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n6, [ubuntu, gcc], (arm64, 448), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [echoDot]).

link(n5, n13, 15.0, 143).
link(n13, n5, 15.0, 143).
link(n2, n15, 15.0, 24).
link(n15, n2, 15.0, 24).
link(n5, n8, 13, 232).
link(n8, n5, 13, 232).
link(n3, n14, 18.0, 97).
link(n14, n3, 18.0, 97).
link(n6, n15, 14.0, 448).
link(n15, n6, 14.0, 448).
link(n1, n13, 5, 302).
link(n13, n1, 5, 302).
link(n0, n14, 10, 226).
link(n14, n0, 10, 226).
link(n7, n11, 17.0, 432).
link(n11, n7, 17.0, 432).
link(n7, n8, 15.0, 201).
link(n8, n7, 15.0, 201).
link(n0, n8, 9, 62).
link(n8, n0, 9, 62).
link(n11, n12, 23.0, 427).
link(n12, n11, 23.0, 427).
link(n7, n9, 15, 430).
link(n9, n7, 15, 430).
link(n6, n14, 14.0, 256).
link(n14, n6, 14.0, 256).
link(n0, n10, 7, 435).
link(n10, n0, 7, 435).
link(n7, n7, 0.0, inf).
link(n2, n9, 15.0, 60).
link(n9, n2, 15.0, 60).
link(n9, n14, 14.0, 117).
link(n14, n9, 14.0, 117).
link(n10, n12, 21.0, 58).
link(n12, n10, 21.0, 58).
link(n11, n14, 12.0, 166).
link(n14, n11, 12.0, 166).
link(n6, n13, 12, 112).
link(n13, n6, 12, 112).
link(n0, n15, 12.0, 294).
link(n15, n0, 12.0, 294).
link(n10, n10, 0.0, inf).
link(n1, n3, 15.0, 193).
link(n3, n1, 15.0, 193).
link(n4, n13, 17.0, 102).
link(n13, n4, 17.0, 102).
link(n5, n6, 9, 208).
link(n6, n5, 9, 208).
link(n4, n12, 15, 434).
link(n12, n4, 15, 434).
link(n5, n11, 16.0, 496).
link(n11, n5, 16.0, 496).
link(n12, n15, 20.0, 395).
link(n15, n12, 20.0, 395).
link(n2, n14, 13.0, 463).
link(n14, n2, 13.0, 463).
link(n3, n10, 5, 379).
link(n10, n3, 5, 379).
link(n2, n5, 6.0, 497).
link(n5, n2, 6.0, 497).
link(n3, n3, 0.0, inf).
link(n2, n10, 10.0, 206).
link(n10, n2, 10.0, 206).
link(n2, n6, 15.0, 339).
link(n6, n2, 15.0, 339).
link(n0, n6, 12.0, 244).
link(n6, n0, 12.0, 244).
link(n4, n10, 6, 109).
link(n10, n4, 6, 109).
link(n6, n7, 7, 48).
link(n7, n6, 7, 48).
link(n0, n1, 14, 75).
link(n1, n0, 14, 75).
link(n3, n8, 17.0, 329).
link(n8, n3, 17.0, 329).
link(n1, n12, 17.0, 84).
link(n12, n1, 17.0, 84).
link(n10, n15, 10, 98).
link(n15, n10, 10, 98).
link(n3, n9, 9, 111).
link(n9, n3, 9, 111).
link(n1, n11, 8.0, 378).
link(n11, n1, 8.0, 378).
link(n5, n14, 13.0, 156).
link(n14, n5, 13.0, 156).
link(n8, n15, 3, 104).
link(n15, n8, 3, 104).
link(n2, n3, 11.0, 321).
link(n3, n2, 11.0, 321).
link(n8, n9, 8.0, 29).
link(n9, n8, 8.0, 29).
link(n5, n12, 17, 228).
link(n12, n5, 17, 228).
link(n15, n15, 0.0, inf).
link(n3, n5, 19, 407).
link(n5, n3, 19, 407).
link(n8, n11, 6, 126).
link(n11, n8, 6, 126).
link(n4, n7, 9, 479).
link(n7, n4, 9, 479).
link(n9, n13, 11.0, 160).
link(n13, n9, 11.0, 160).
link(n4, n11, 12, 34).
link(n11, n4, 12, 34).
link(n8, n8, 0.0, inf).
link(n6, n6, 0.0, inf).
link(n0, n0, 0.0, inf).
link(n14, n15, 9.0, 431).
link(n15, n14, 9.0, 431).
link(n11, n11, 0.0, inf).
link(n9, n11, 2, 469).
link(n11, n9, 2, 469).
link(n7, n15, 13, 330).
link(n15, n7, 13, 330).
link(n3, n12, 23.0, 72).
link(n12, n3, 23.0, 72).
link(n8, n10, 13.0, 117).
link(n10, n8, 13.0, 117).
link(n10, n13, 19.0, 363).
link(n13, n10, 19.0, 363).
link(n4, n6, 12, 168).
link(n6, n4, 12, 168).
link(n0, n12, 17.0, 43).
link(n12, n0, 17.0, 43).
link(n7, n12, 18.0, 216).
link(n12, n7, 18.0, 216).
link(n4, n8, 11.0, 417).
link(n8, n4, 11.0, 417).
link(n1, n10, 18.0, 77).
link(n10, n1, 18.0, 77).
link(n5, n10, 10.0, 51).
link(n10, n5, 10.0, 51).
link(n2, n2, 0.0, inf).
link(n2, n13, 18.0, 185).
link(n13, n2, 18.0, 185).
link(n4, n9, 10, 240).
link(n9, n4, 10, 240).
link(n1, n14, 8, 269).
link(n14, n1, 8, 269).
link(n12, n12, 0.0, inf).
link(n1, n7, 10, 391).
link(n7, n1, 10, 391).
link(n4, n5, 4, 469).
link(n5, n4, 4, 469).
link(n2, n12, 20.0, 382).
link(n12, n2, 20.0, 382).
link(n7, n14, 18.0, 479).
link(n14, n7, 18.0, 479).
link(n6, n9, 12.0, 153).
link(n9, n6, 12.0, 153).
link(n0, n13, 15.0, 243).
link(n13, n0, 15.0, 243).
link(n1, n4, 14.0, 269).
link(n4, n1, 14.0, 269).
link(n5, n5, 0.0, inf).
link(n4, n4, 0.0, inf).
link(n1, n6, 6, 171).
link(n6, n1, 6, 171).
link(n10, n11, 16.0, 482).
link(n11, n10, 16.0, 482).
link(n5, n15, 15.0, 418).
link(n15, n5, 15.0, 418).
link(n2, n11, 17.0, 348).
link(n11, n2, 17.0, 348).
link(n8, n12, 17, 333).
link(n12, n8, 17, 333).
link(n8, n14, 6, 294).
link(n14, n8, 6, 294).
link(n2, n7, 13.0, 368).
link(n7, n2, 13.0, 368).
link(n1, n15, 8.0, 363).
link(n15, n1, 8.0, 363).
link(n8, n13, 6, 161).
link(n13, n8, 6, 161).
link(n4, n14, 12.0, 241).
link(n14, n4, 12.0, 241).
link(n3, n11, 12, 279).
link(n11, n3, 12, 279).
link(n3, n6, 12, 126).
link(n6, n3, 12, 126).
link(n6, n8, 16, 484).
link(n8, n6, 16, 484).
link(n13, n15, 9.0, 74).
link(n15, n13, 9.0, 74).
link(n6, n11, 14.0, 456).
link(n11, n6, 14.0, 456).
link(n1, n2, 16.0, 240).
link(n2, n1, 16.0, 240).
link(n0, n2, 3, 89).
link(n2, n0, 3, 89).
link(n5, n9, 14.0, 365).
link(n9, n5, 14.0, 365).
link(n2, n4, 5.0, 317).
link(n4, n2, 5.0, 317).
link(n3, n4, 10.0, 226).
link(n4, n3, 10.0, 226).
link(n9, n12, 23.0, 115).
link(n12, n9, 23.0, 115).
link(n9, n15, 11.0, 197).
link(n15, n9, 11.0, 197).
link(n3, n7, 16.0, 58).
link(n7, n3, 16.0, 58).
link(n12, n14, 23.0, 97).
link(n14, n12, 23.0, 97).
link(n1, n1, 0.0, inf).
link(n10, n14, 17.0, 309).
link(n14, n10, 17.0, 309).
link(n1, n5, 10, 489).
link(n5, n1, 10, 489).
link(n12, n13, 22.0, 299).
link(n13, n12, 22.0, 299).
link(n13, n13, 0.0, inf).
link(n7, n13, 16, 165).
link(n13, n7, 16, 165).
link(n6, n10, 17.0, 103).
link(n10, n6, 17.0, 103).
link(n0, n5, 3, 352).
link(n5, n0, 3, 352).
link(n0, n3, 8, 188).
link(n3, n0, 8, 188).
link(n11, n15, 9.0, 298).
link(n15, n11, 9.0, 298).
link(n3, n15, 17, 157).
link(n15, n3, 17, 157).
link(n0, n11, 14.0, 424).
link(n11, n0, 14.0, 424).
link(n7, n10, 11, 126).
link(n10, n7, 11, 126).
link(n3, n13, 20.0, 49).
link(n13, n3, 20.0, 49).
link(n1, n9, 6, 300).
link(n9, n1, 6, 300).
link(n9, n10, 14.0, 71).
link(n10, n9, 14.0, 71).
link(n14, n14, 0.0, inf).
link(n0, n4, 2, 165).
link(n4, n0, 2, 165).
link(n11, n13, 12.0, 207).
link(n13, n11, 12.0, 207).
link(n1, n8, 5, 204).
link(n8, n1, 5, 204).
link(n0, n7, 10.0, 334).
link(n7, n0, 10.0, 334).
link(n13, n14, 8, 392).
link(n14, n13, 8, 392).
link(n0, n9, 12.0, 198).
link(n9, n0, 12.0, 198).
link(n9, n9, 0.0, inf).
link(n2, n8, 12.0, 288).
link(n8, n2, 12.0, 288).
link(n6, n12, 11, 340).
link(n12, n6, 11, 340).
link(n5, n7, 7, 49).
link(n7, n5, 7, 49).
link(n4, n15, 14.0, 281).
link(n15, n4, 14.0, 281).

nodeType(n0, edge).
nodeType(n1, cloud).
nodeType(n2, edge).
nodeType(n3, thing).
nodeType(n4, edge).
nodeType(n5, thing).
nodeType(n6, thing).
nodeType(n7, thing).
nodeType(n8, thing).
nodeType(n9, edge).
nodeType(n10, cloud).
nodeType(n11, thing).
nodeType(n12, edge).
nodeType(n13, edge).
nodeType(n14, thing).
nodeType(n15, thing).

location(n0, it).
location(n1, es).
location(n2, it).
location(n3, it).
location(n4, es).
location(n5, it).
location(n6, it).
location(n7, de).
location(n8, it).
location(n9, de).
location(n10, de).
location(n11, it).
location(n12, it).
location(n13, es).
location(n14, it).
location(n15, de).

provider(n0, aws).
provider(n1, aws).
provider(n2, ibm).
provider(n3, ibm).
provider(n4, ibm).
provider(n5, ibm).
provider(n6, ibm).
provider(n7, ibm).
provider(n8, aws).
provider(n9, aws).
provider(n10, aws).
provider(n11, ibm).
provider(n12, azure).
provider(n13, ibm).
provider(n14, aws).
provider(n15, azure).
