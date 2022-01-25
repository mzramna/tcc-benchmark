CREATE ROLE usuarios ;
ALTER ROLE usuarios SUPERUSER CREATEDB NOCREATEROLE INHERIT LOGIN;

GRANT usuarios to mzramna;
ALTER SCHEMA public owner to usuarios;
GRANT ALL ON SCHEMA public TO usuarios;
GRANT ALL privileges  on all tables IN SCHEMA public TO usuarios;

drop USER  ibd4bhkjpyi4hx;
CREATE USER  ibd4bhkjpyi4hx WITH PASSWORD 'mls83mfbsdnvte';
GRANT usuarios to ibd4bhkjpyi4hx;

drop USER  fhabpsyubkgo7;
CREATE USER  fhabpsyubkgo7 WITH PASSWORD 'chv9jtnv2r98zw';
GRANT usuarios to fhabpsyubkgo7;

drop USER  rg2dsvhc6ahajz;
CREATE USER  rg2dsvhc6ahajz WITH PASSWORD 'vpzg49u3qaeckl';
GRANT usuarios to rg2dsvhc6ahajz;

drop USER  cu9c5qycens55v;
CREATE USER  cu9c5qycens55v WITH PASSWORD 'lqr9zrhste5ve6';
GRANT usuarios to cu9c5qycens55v;

drop USER  vaddpet2mh7hiq;
CREATE USER  vaddpet2mh7hiq WITH PASSWORD 'p3vqtklfgpnver';
GRANT usuarios to vaddpet2mh7hiq;

drop USER  nyq9kedfwus9d;
CREATE USER  nyq9kedfwus9d WITH PASSWORD 'tcf6mwpy2ixeex';
GRANT usuarios to nyq9kedfwus9d;

drop USER  loymzy83yf9kub;
CREATE USER  loymzy83yf9kub WITH PASSWORD 'jrffhw8kcpxgzg';
GRANT usuarios to loymzy83yf9kub;

drop USER  dvjr3ef9uwukby;
CREATE USER  dvjr3ef9uwukby WITH PASSWORD 'wwz54szihhwmie';
GRANT usuarios to dvjr3ef9uwukby;

drop USER  b2cr7y3twxkfzn;
CREATE USER  b2cr7y3twxkfzn WITH PASSWORD 'qxeu6hkv9craqb';
GRANT usuarios to b2cr7y3twxkfzn;

drop USER  c7f5w3xj54poop;
CREATE USER  c7f5w3xj54poop WITH PASSWORD 'nwgtnbwup9pltj';
GRANT usuarios to c7f5w3xj54poop;

ALTER TABLE public.actor  owner to usuarios;
ALTER TABLE public.address  owner to usuarios;
ALTER TABLE public.category  owner to usuarios;
ALTER TABLE public.city  owner to usuarios;
ALTER TABLE public.country  owner to usuarios;
ALTER TABLE public.customer  owner to usuarios;
ALTER TABLE public.film  owner to usuarios;
ALTER TABLE public.film_actor  owner to usuarios;
ALTER TABLE public.film_category  owner to usuarios;
ALTER TABLE public.inventory  owner to usuarios;
ALTER TABLE public."language"  owner to usuarios;
ALTER TABLE public.payment  owner to usuarios;
ALTER TABLE public.rental  owner to usuarios;
ALTER TABLE public.staff  owner to usuarios;
ALTER TABLE public.store  owner to usuarios;

GRANT ALL ON TABLE public.actor TO usuarios;
GRANT ALL ON TABLE public.address TO usuarios;
GRANT ALL ON TABLE public.category TO usuarios;
GRANT ALL ON TABLE public.city TO usuarios;
GRANT ALL ON TABLE public.country TO usuarios;
GRANT ALL ON TABLE public.customer TO usuarios;
GRANT ALL ON TABLE public.film TO usuarios;
GRANT ALL ON TABLE public.film_actor TO usuarios;
GRANT ALL ON TABLE public.film_category TO usuarios;
GRANT ALL ON TABLE public.inventory TO usuarios;
GRANT ALL ON TABLE public."language" TO usuarios;
GRANT ALL ON TABLE public.payment TO usuarios;
GRANT ALL ON TABLE public.rental TO usuarios;
GRANT ALL ON TABLE public.staff TO usuarios;
GRANT ALL ON TABLE public.store TO usuarios;
