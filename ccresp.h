#ifndef CCRESP_H
#define CCRESP_H

#include "ccpert.h"

using namespace std;

namespace psi { namespace ccreorg {

class CCResp {
public:
  CCResp(shared_ptr<CCPert> Y, shared_ptr<CCPert> X);
  CCResp(shared_ptr<CCPert> X);
  ~CCResp();
  double linresp(shared_ptr<CCPert> Y, shared_ptr<CCPert> X);

protected:
  shared_ptr<Hamiltonian> H_;
  shared_ptr<CCWfn> CC_;
  shared_ptr<HBAR> HBAR_;
  shared_ptr<CCLambda> Lambda_;

  int no_;
  int nv_;
  shared_ptr<CCPert> Y_;
  shared_ptr<CCPert> X_;
};

}} // psi::ccreorgc

#endif
