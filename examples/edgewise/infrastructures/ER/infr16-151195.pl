bwTh(3).
hwTh(1).

node(n10, [python, ubuntu, mySQL], (x86, 608), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n13, [ubuntu, mySQL, python, js, gcc], (x86, 672), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n3, [js, python], (arm64, 512), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [soil, echoDot]).
node(n0, [mySQL, python, ubuntu, js], (x86, 448), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [arViewer, water]).
node(n15, [mySQL, js], (arm64, 448), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n8, [gcc, ubuntu], (x86, 608), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [heat]).
node(n12, [ubuntu, mySQL, python, js, gcc], (arm64, 416), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n5, [ubuntu, python, mySQL], (x86, 448), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [energy]).
node(n14, [gcc, ubuntu], (arm64, 608), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n2, [python, gcc, ubuntu], (x86, 384), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [iphoneXS, piCamera1]).
node(n9, [mySQL], (x86, 928), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n1, [mySQL, ubuntu, python], (x86, 608), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [cam11]).
node(n6, [ubuntu], (arm64, 640), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [cam22, cam21]).
node(n7, [python], (arm64, 640), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [cam12]).
node(n11, [ubuntu, gcc, python, js], (x86, 672), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n4, [mySQL, gcc, js, python], (arm64, 384), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [piCamera2, nutrient]).

link(n2, n13, 17.0, 64).
link(n13, n2, 17.0, 64).
link(n6, n9, 33.0, 461).
link(n9, n6, 33.0, 461).
link(n4, n11, 30.0, 430).
link(n11, n4, 30.0, 430).
link(n4, n6, 36.0, 165).
link(n6, n4, 36.0, 165).
link(n7, n7, 0.0, inf).
link(n1, n14, 18.0, 463).
link(n14, n1, 18.0, 463).
link(n6, n8, 23.0, 35).
link(n8, n6, 23.0, 35).
link(n2, n15, 17, 386).
link(n15, n2, 17, 386).
link(n0, n5, 26.0, 191).
link(n5, n0, 26.0, 191).
link(n9, n11, 17.0, 54).
link(n11, n9, 17.0, 54).
link(n8, n12, 14, 311).
link(n12, n8, 14, 311).
link(n12, n15, 20.0, 283).
link(n15, n12, 20.0, 283).
link(n0, n1, 30.0, 95).
link(n1, n0, 30.0, 95).
link(n2, n12, 19.0, 473).
link(n12, n2, 19.0, 473).
link(n12, n13, 12, 45).
link(n13, n12, 12, 45).
link(n4, n5, 29.0, 373).
link(n5, n4, 29.0, 373).
link(n13, n15, 8, 467).
link(n15, n13, 8, 467).
link(n1, n2, 25.0, 341).
link(n2, n1, 25.0, 341).
link(n3, n5, 30.0, 321).
link(n5, n3, 30.0, 321).
link(n7, n8, 24.0, 45).
link(n8, n7, 24.0, 45).
link(n4, n9, 13, 21).
link(n9, n4, 13, 21).
link(n9, n15, 34.0, 412).
link(n15, n9, 34.0, 412).
link(n0, n12, 24.0, 356).
link(n12, n0, 24.0, 356).
link(n4, n12, 17.0, 219).
link(n12, n4, 17.0, 219).
link(n10, n12, 18.0, 119).
link(n12, n10, 18.0, 119).
link(n7, n11, 28.0, 51).
link(n11, n7, 28.0, 51).
link(n4, n13, 18, 476).
link(n13, n4, 18, 476).
link(n11, n15, 24.0, 378).
link(n15, n11, 24.0, 378).
link(n4, n8, 23.0, 250).
link(n8, n4, 23.0, 250).
link(n8, n10, 13, 112).
link(n10, n8, 13, 112).
link(n2, n3, 19.0, 455).
link(n3, n2, 19.0, 455).
link(n3, n12, 18.0, 242).
link(n12, n3, 18.0, 242).
link(n4, n7, 13.0, 236).
link(n7, n4, 13.0, 236).
link(n3, n6, 37.0, 334).
link(n6, n3, 37.0, 334).
link(n7, n14, 5, 382).
link(n14, n7, 5, 382).
link(n0, n14, 15.0, 108).
link(n14, n0, 15.0, 108).
link(n3, n4, 17.0, 348).
link(n4, n3, 17.0, 348).
link(n3, n9, 30.0, 109).
link(n9, n3, 30.0, 109).
link(n5, n10, 24.0, 441).
link(n10, n5, 24.0, 441).
link(n7, n9, 26.0, 107).
link(n9, n7, 26.0, 107).
link(n6, n7, 23.0, 176).
link(n7, n6, 23.0, 176).
link(n6, n13, 23.0, 390).
link(n13, n6, 23.0, 390).
link(n3, n8, 31.0, 411).
link(n8, n3, 31.0, 411).
link(n4, n4, 0.0, inf).
link(n5, n9, 40.0, 309).
link(n9, n5, 40.0, 309).
link(n10, n13, 8, 375).
link(n13, n10, 8, 375).
link(n14, n15, 13.0, 68).
link(n15, n14, 13.0, 68).
link(n1, n11, 29.0, 256).
link(n11, n1, 29.0, 256).
link(n8, n13, 21.0, 483).
link(n13, n8, 21.0, 483).
link(n13, n13, 0.0, inf).
link(n8, n15, 29.0, 402).
link(n15, n8, 29.0, 402).
link(n6, n15, 15.0, 489).
link(n15, n6, 15.0, 489).
link(n0, n7, 10, 180).
link(n7, n0, 10, 180).
link(n1, n1, 0.0, inf).
link(n2, n5, 21.0, 447).
link(n5, n2, 21.0, 447).
link(n5, n5, 0.0, inf).
link(n4, n14, 8, 452).
link(n14, n4, 8, 452).
link(n5, n7, 16.0, 327).
link(n7, n5, 16.0, 327).
link(n0, n8, 34.0, 496).
link(n8, n0, 34.0, 496).
link(n0, n10, 21.0, 44).
link(n10, n0, 21.0, 44).
link(n11, n13, 16, 145).
link(n13, n11, 16, 145).
link(n0, n6, 33.0, 168).
link(n6, n0, 33.0, 168).
link(n8, n11, 7, 78).
link(n11, n8, 7, 78).
link(n13, n14, 17.0, 58).
link(n14, n13, 17.0, 58).
link(n1, n12, 27.0, 361).
link(n12, n1, 27.0, 361).
link(n2, n2, 0.0, inf).
link(n5, n6, 7, 64).
link(n6, n5, 7, 64).
link(n4, n15, 21.0, 221).
link(n15, n4, 21.0, 221).
link(n7, n13, 12, 253).
link(n13, n7, 12, 253).
link(n3, n10, 18.0, 22).
link(n10, n3, 18.0, 22).
link(n6, n14, 28.0, 487).
link(n14, n6, 28.0, 487).
link(n5, n13, 16.0, 112).
link(n13, n5, 16.0, 112).
link(n10, n15, 16.0, 352).
link(n15, n10, 16.0, 352).
link(n3, n7, 14.0, 122).
link(n7, n3, 14.0, 122).
link(n3, n14, 9, 493).
link(n14, n3, 9, 493).
link(n1, n4, 11, 183).
link(n4, n1, 11, 183).
link(n10, n10, 0.0, inf).
link(n1, n7, 20.0, 473).
link(n7, n1, 20.0, 473).
link(n10, n11, 20.0, 137).
link(n11, n10, 20.0, 137).
link(n8, n14, 22.0, 261).
link(n14, n8, 22.0, 261).
link(n1, n9, 24.0, 394).
link(n9, n1, 24.0, 394).
link(n9, n14, 21.0, 227).
link(n14, n9, 21.0, 227).
link(n5, n8, 30.0, 324).
link(n8, n5, 30.0, 324).
link(n11, n11, 0.0, inf).
link(n14, n14, 0.0, inf).
link(n5, n14, 21.0, 26).
link(n14, n5, 21.0, 26).
link(n0, n3, 24.0, 351).
link(n3, n0, 24.0, 351).
link(n1, n5, 33.0, 484).
link(n5, n1, 33.0, 484).
link(n8, n9, 10, 252).
link(n9, n8, 10, 252).
link(n0, n11, 38.0, 296).
link(n11, n0, 38.0, 296).
link(n0, n2, 15.0, 35).
link(n2, n0, 15.0, 35).
link(n2, n6, 28.0, 146).
link(n6, n2, 28.0, 146).
link(n9, n10, 23.0, 251).
link(n10, n9, 23.0, 251).
link(n2, n8, 29.0, 146).
link(n8, n2, 29.0, 146).
link(n6, n10, 31.0, 57).
link(n10, n6, 31.0, 57).
link(n12, n12, 0.0, inf).
link(n7, n10, 11, 447).
link(n10, n7, 11, 447).
link(n6, n6, 0.0, inf).
link(n6, n12, 35.0, 63).
link(n12, n6, 35.0, 63).
link(n0, n9, 32.0, 309).
link(n9, n0, 32.0, 309).
link(n9, n12, 24.0, 291).
link(n12, n9, 24.0, 291).
link(n3, n3, 0.0, inf).
link(n1, n3, 27.0, 415).
link(n3, n1, 27.0, 415).
link(n3, n15, 22.0, 168).
link(n15, n3, 22.0, 168).
link(n4, n10, 17.0, 491).
link(n10, n4, 17.0, 491).
link(n15, n15, 0.0, inf).
link(n12, n14, 9, 397).
link(n14, n12, 9, 397).
link(n1, n8, 22.0, 239).
link(n8, n1, 22.0, 239).
link(n2, n11, 33.0, 411).
link(n11, n2, 33.0, 411).
link(n8, n8, 0.0, inf).
link(n2, n10, 16.0, 225).
link(n10, n2, 16.0, 225).
link(n0, n15, 18.0, 377).
link(n15, n0, 18.0, 377).
link(n1, n15, 25.0, 144).
link(n15, n1, 25.0, 144).
link(n0, n4, 19, 300).
link(n4, n0, 19, 300).
link(n2, n7, 5, 457).
link(n7, n2, 5, 457).
link(n5, n11, 23.0, 391).
link(n11, n5, 23.0, 391).
link(n1, n10, 9, 241).
link(n10, n1, 9, 241).
link(n2, n9, 31.0, 133).
link(n9, n2, 31.0, 133).
link(n7, n15, 8, 356).
link(n15, n7, 8, 356).
link(n2, n4, 18.0, 160).
link(n4, n2, 18.0, 160).
link(n7, n12, 14.0, 94).
link(n12, n7, 14.0, 94).
link(n9, n9, 0.0, inf).
link(n5, n15, 8, 184).
link(n15, n5, 8, 184).
link(n3, n11, 38.0, 466).
link(n11, n3, 38.0, 466).
link(n6, n11, 16, 355).
link(n11, n6, 16, 355).
link(n5, n12, 28.0, 99).
link(n12, n5, 28.0, 99).
link(n11, n12, 21.0, 295).
link(n12, n11, 21.0, 295).
link(n9, n13, 31.0, 444).
link(n13, n9, 31.0, 444).
link(n10, n14, 9, 324).
link(n14, n10, 9, 324).
link(n0, n0, 0.0, inf).
link(n1, n13, 17.0, 291).
link(n13, n1, 17.0, 291).
link(n0, n13, 22.0, 136).
link(n13, n0, 22.0, 136).
link(n1, n6, 40.0, 24).
link(n6, n1, 40.0, 24).
link(n11, n14, 29.0, 97).
link(n14, n11, 29.0, 97).
link(n2, n14, 10.0, 427).
link(n14, n2, 10.0, 427).
link(n3, n13, 26.0, 237).
link(n13, n3, 26.0, 237).

nodeType(n0, edge).
nodeType(n1, thing).
nodeType(n2, thing).
nodeType(n3, thing).
nodeType(n4, edge).
nodeType(n5, thing).
nodeType(n6, thing).
nodeType(n7, thing).
nodeType(n8, edge).
nodeType(n9, thing).
nodeType(n10, edge).
nodeType(n11, edge).
nodeType(n12, cloud).
nodeType(n13, cloud).
nodeType(n14, edge).
nodeType(n15, thing).

location(n0, de).
location(n1, de).
location(n2, it).
location(n3, de).
location(n4, it).
location(n5, de).
location(n6, de).
location(n7, es).
location(n8, it).
location(n9, it).
location(n10, de).
location(n11, es).
location(n12, it).
location(n13, es).
location(n14, it).
location(n15, es).

provider(n0, ibm).
provider(n1, ibm).
provider(n2, ibm).
provider(n3, azure).
provider(n4, azure).
provider(n5, aws).
provider(n6, ibm).
provider(n7, azure).
provider(n8, azure).
provider(n9, ibm).
provider(n10, ibm).
provider(n11, azure).
provider(n12, azure).
provider(n13, azure).
provider(n14, aws).
provider(n15, azure).
